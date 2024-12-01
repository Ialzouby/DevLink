from faker import Faker
from urlbox import webhook_validator
from urlbox import InvalidHeaderSignatureError
import datetime
import json
import hmac
import pytest
from hashlib import sha256

fake = Faker()

timestamp_one_minute_ago = int(
    datetime.datetime.timestamp(
        datetime.datetime.now() - datetime.timedelta(minutes=1)
    )
)

webhook_secret = fake.pystr()

header_signature = f"t={timestamp_one_minute_ago},sha256=1e1b3c7f6b5f60f7b44ed1a85e653769ecf0c41ec5c7e8c131fc1a20357cc2b1"

payload = {
    "event": "render.succeeded",
    "renderId": "794383cd-b09e-4aef-a12b-fadf8aad9d63",
    "result": {
        "renderUrl": "https://renders.urlbox.io/urlbox1/renders/61431b47b8538a00086c29dd/2021/11/24/bee42850-bab6-43c6-bd9d-e614581d31b4.png"
    },
    "meta": {
        "startTime": "2021-11-24T16:49:48.307Z",
        "endTime": "2021-11-24T16:49:53.659Z",
    },
}


def test_call_valid_webhook():
    # Dynamically generate header signature to make the crypto comparision pass
    payload_json_string = json.dumps(payload, separators=(",", ":"))

    signature_generated = hmac.new(
        webhook_secret.encode("utf-8"),
        msg=f"{timestamp_one_minute_ago}.{payload_json_string}".encode(
            "utf-8"
        ),
        digestmod=sha256,
    ).hexdigest()

    header_signature = (
        f"t={timestamp_one_minute_ago},sha256={signature_generated}"
    )

    assert (
        webhook_validator.call(header_signature, payload, webhook_secret)
        is True
    )


def test_call_invalid_signature():
    header_signature = fake.pystr()

    with pytest.raises(InvalidHeaderSignatureError) as exception:
        webhook_validator.call(header_signature, payload, webhook_secret)


def test_call_invalid_hash_mismatch():
    header_signature = f"t={timestamp_one_minute_ago},sha256=930ee08957512f247e289703ac951fc60da1e2d12919bfd518d90513b0687ee0"

    with pytest.raises(InvalidHeaderSignatureError) as exception:
        webhook_validator.call(header_signature, payload, webhook_secret)

    assert "Invalid signature" in str(exception.value)


def test_call_invalid_hash_regex_catch():
    header_signature = f"t={timestamp_one_minute_ago},sha256={fake.pystr()}"

    with pytest.raises(InvalidHeaderSignatureError) as exception:
        webhook_validator.call(header_signature, payload, webhook_secret)

    assert "Invalid signature" in str(exception.value)


def test_call_invalid_timestamp():
    header_signature = f"t={fake.pystr()},sha256=930ee08957512f247e289703ac951fc60da1e2d12919bfd518d90513b0687ee0"

    with pytest.raises(Exception) as exception:
        webhook_validator.call(header_signature, payload, webhook_secret)

    assert "Invalid timestamp" in str(exception.value)


def test_call_invalid_timestamp_timing_attack():
    timestamp_ten_minute_ago = int(
        datetime.datetime.timestamp(
            datetime.datetime.now() - datetime.timedelta(minutes=10)
        )
    )

    header_signature = f"t={timestamp_ten_minute_ago},sha256=930ee08957512f247e289703ac951fc60da1e2d12919bfd518d90513b0687ee0"

    with pytest.raises(InvalidHeaderSignatureError) as exception:
        webhook_validator.call(header_signature, payload, webhook_secret)

    assert "Invalid timestamp" in str(exception.value)
