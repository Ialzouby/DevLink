import datetime
import json
import hmac
import re
from hashlib import sha256
from urlbox import InvalidHeaderSignatureError

SIGNATURE_REGEX = "^sha256=[0-9a-zA-Z]{40,}$"
TIMESTAMP_REGEX = "^t=[0-9]+$"
WEBHOOK_AGE_MAX_MINUTES = 5


def call(header_signature, payload, webhook_secret):
    """
      Returns True or raises a InvalidHeaderSignatureError depending upon if the header signature is part of a valid UrlBox webhook request.

      :param header_signature: x-urlbox-signature header from the Urlbox request to the client's webhook endpoint.

      :param payload: json body of the webhook request.

      :param webhook_secret: Your webhook secret found in your Urlbox (NB: NOT the api secret - that's a different secret)
      Dashboard`https://urlbox.io/dashboard/api`

      This function parses the signature value to determine if it's part of a valid Urlbox webhook request.
    """

    try:
        timestamp, signature = header_signature.split(",")
    except ValueError as e:
        raise (InvalidHeaderSignatureError())

    _check_timestamp(timestamp)
    _check_signature(signature, timestamp, payload, webhook_secret)

    return True


def _check_signature(raw_signature, timestamp, payload, webhook_secret):
    if not re.search(SIGNATURE_REGEX, raw_signature):
        raise (InvalidHeaderSignatureError("Invalid signature"))

    signature_webhook = raw_signature.split("=")[1]
    timestamp = int(timestamp.split("=")[1])

    payload_json_string = json.dumps(payload, separators=(",", ":"))

    signature_generated = hmac.new(
        webhook_secret.encode("utf-8"),
        msg=f"{timestamp}.{payload_json_string}".encode("utf-8"),
        digestmod=sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature_generated, signature_webhook):
        raise (InvalidHeaderSignatureError("Invalid signature"))


def _check_timestamp(timestamp):
    if not re.search(TIMESTAMP_REGEX, timestamp):
        raise (InvalidHeaderSignatureError("Invalid timestamp"))

    timestamp = int(timestamp.split("=")[1])

    _check_webhook_creation_time(timestamp)


def _check_webhook_creation_time(timestamp):
    header_datetime = datetime.datetime.utcfromtimestamp(timestamp)

    current_datetime = datetime.datetime.utcnow()

    webhook_posted = current_datetime - header_datetime
    webhook_posted_minutes_ago = webhook_posted.total_seconds() / 60

    if webhook_posted_minutes_ago > WEBHOOK_AGE_MAX_MINUTES:
        raise (InvalidHeaderSignatureError("Invalid timestamp"))
