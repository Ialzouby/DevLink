from faker import Faker
from hashlib import sha1
from urlbox import InvalidUrlException, UrlboxClient
import json
import hmac
import pytest
import random
import requests
import requests_mock
import urllib.parse
import warnings


fake = Faker()

# test_init()
def test_only_api_key_provided():
    api_key = fake.pystr()
    urlbox_client = UrlboxClient(api_key=api_key)

    assert urlbox_client.api_key == api_key


def test_both_api_key_and_api_secret_provided():
    api_key = fake.pystr()
    api_secret = fake.pystr()
    urlbox_client = UrlboxClient(api_key=api_key, api_secret=api_secret)

    assert (
        urlbox_client.api_key == api_key
        and urlbox_client.api_secret == api_secret
    )


def test_api_key_not_provided():
    with pytest.raises(TypeError) as type_error:
        UrlboxClient()

    assert (
        str(type_error.value)
        == "__init__() missing 1 required keyword-only argument: 'api_key'"
    )


# Test get()
# valid api key
# valid url, format and options
def test_get_successful():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/{format}"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert format in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)


def test_get_successful_authenticated():
    api_key = fake.pystr()
    api_secret = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
        "header": ["header1=value1", "header2=value2"],
    }
    url_encoded_options = urllib.parse.urlencode(options, doseq=True)

    token = (
        hmac.new(
            str.encode(api_secret), str.encode(url_encoded_options), sha1,
        )
        .hexdigest()
        .rstrip("\n")
    )

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{token}/{format}"
        f"?{url_encoded_options}"
    )

    urlbox_client = UrlboxClient(api_key=api_key, api_secret=api_secret)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/{format}"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert format in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)


def test_get_with_header_array_in_options():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
        "header": [
            "x-my-first-header=somevalue",
            "x-my-second-header=someothervalue",
        ],
    }

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/{format}"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert format in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)

            assert (
                "header=x-my-first-header%3Dsomevalue&header=x-my-second-header%3Dsomeothervalue"
                in urlbox_request_url
            )


# valid url but with white spaces before and after
def test_get_successful_white_space_url():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )

    url = fake.url()
    url_with_white_spaces = f"  {url}   "

    options = {
        "url": url_with_white_spaces,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    options_parsed = options.copy()
    options_parsed["url"] = url

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options_parsed, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/{format}"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert format in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)


def test_get_successful_without_setting_format():
    api_key = fake.pystr()

    url = fake.url()

    options = {
        "url": url,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/png"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/png"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert "image/png" in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)


def test_get_successful_missing_schema_url():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )

    url_original = "twitter.com"
    url_with_schema = f"http://{url_original}"

    options = {
        "url": url_original,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    options_parsed = options.copy()
    options_parsed["url"] = url_with_schema

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options_parsed, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/{format}"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert format in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)


def test_get_invalid_url():
    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.address()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_client = UrlboxClient(api_key=fake.pystr())

    with pytest.raises(InvalidUrlException) as invalid_url_exception:
        urlbox_client.get(options)

    assert url in str(invalid_url_exception.value)


def test_get_with_different_host_name():
    api_host_name = random.choice(["api-eu.urlbox.io", "api-direct.urlbox.io"])
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"https://{api_host_name}/"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key, api_host_name=api_host_name)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/{format}"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert format in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)


def test_get_successful_with_html_not_url():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )

    html = "<html><head></head><body><h1>TEST</h1></body></html>"

    options = {"html": html, "format": format}

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        with open(
            "tests/files/urlbox_screenshot.png", "rb"
        ) as urlbox_screenshot:
            requests_mocker.get(
                urlbox_request_url,
                content=urlbox_screenshot.read(),
                headers={"content-type": f"image/{format}"},
            )

            response = urlbox_client.get(options)

            assert response.status_code == 200
            assert format in response.headers["Content-Type"]
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)


def test_get_unsuccessful_without_html_not_url():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )

    options = {"format": format}

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with pytest.raises(KeyError) as missing_key_exception:
        urlbox_client.get(options)

    assert "Missing 'url' or 'html' key in options" in str(
        missing_key_exception.value
    )


# DELETE
def test_delete_request():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {"url": url, "format": format}

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.delete(
            urlbox_request_url, headers={"content-type": f"image/{format}"}
        )

        response = urlbox_client.delete(options)

        assert response.status_code == 200
        assert format in response.headers["Content-Type"]
        assert isinstance(response, requests.models.Response)


# HEAD
def test_head_request():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key)

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.head(
            urlbox_request_url,
            content=b"",
            headers={"content-type": f"image/{format}"},
        )

        response = urlbox_client.head(options)

        assert response.status_code == 200
        assert format in response.headers["Content-Type"]
        assert isinstance(response, requests.models.Response)
        assert isinstance(response.content, bytes)
        assert len(response.content) == 0


def test_head_with_different_host_name():
    api_host_name = random.choice(["api-eu.urlbox.io", "api-direct.urlbox.io"])
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"https://{api_host_name}/"
        f"{api_key}/{format}"
        f"?{urllib.parse.urlencode(options, doseq=True)}"
    )

    urlbox_client = UrlboxClient(api_key=api_key, api_host_name=api_host_name)

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.head(
            urlbox_request_url,
            content=b"",
            headers={"content-type": f"image/{format}"},
        )

        response = urlbox_client.head(options)

        assert response.status_code == 200
        assert format in response.headers["Content-Type"]
        assert isinstance(response, requests.models.Response)
        assert isinstance(response.content, bytes)
        assert len(response.content) == 0


# POST
def test_post_request_successful():
    api_key = fake.pystr()
    api_secret = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )

    options = {
        "url": fake.url(),
        "webhook_url": f"{fake.url()}/webook",
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}{UrlboxClient.POST_END_POINT}"
    )

    urlbox_client = UrlboxClient(api_key=api_key, api_secret=api_secret)

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.post(
            urlbox_request_url,
            content=b'{"status":"created","renderId":"47dd4b7b-1eea-437c-ade0-f2d1cd7bf5a1","statusUrl":"https://api.urlbox.io/render/47dd4b7b-1eea-437c-ade0-f2d1cd7bf5a1"}',
            headers={"content-type": "application/json"},
            status_code=201,
        )

        response = urlbox_client.post(options)

        assert response.status_code == 201
        assert isinstance(response, requests.models.Response)
        assert isinstance(response.content, bytes)


def test_post_with_different_host_name():
    api_host_name = random.choice(["api-eu.urlbox.io", "api-direct.urlbox.io"])
    api_key = fake.pystr()
    api_secret = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": fake.url(),
        "webhook_url": f"{fake.url()}/webook",
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"https://{api_host_name}/{UrlboxClient.POST_END_POINT}"
    )

    urlbox_client = UrlboxClient(
        api_key=api_key, api_secret=api_secret, api_host_name=api_host_name
    )

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.post(
            urlbox_request_url,
            content=b'{"status":"created","renderId":"47dd4b7b-1eea-437c-ade0-f2d1cd7bf5a1","statusUrl":"https://api.urlbox.io/render/47dd4b7b-1eea-437c-ade0-f2d1cd7bf5a1"}',
            headers={"content-type": "application/json"},
            status_code=201,
        )

        response = urlbox_client.post(options)

        assert response.status_code == 201
        assert isinstance(response, requests.models.Response)
        assert isinstance(response.content, bytes)


def test_post_request_successful_missing_webhook_url():
    api_key = fake.pystr()
    api_secret = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )

    options = {
        "url": fake.url(),
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_request_url = (
        f"{UrlboxClient.BASE_API_URL}{UrlboxClient.POST_END_POINT}"
    )

    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.post(
            urlbox_request_url,
            content=b'{"status":"created","renderId":"47dd4b7b-1eea-437c-ade0-f2d1cd7bf5a1","statusUrl":"https://api.urlbox.io/render/47dd4b7b-1eea-437c-ade0-f2d1cd7bf5a1"}',
            headers={"content-type": "application/json"},
            status_code=201,
        )

        urlbox_client = UrlboxClient(api_key=api_key, api_secret=api_secret)

        with warnings.catch_warnings(record=True) as warning:
            response = urlbox_client.post(options)

            # Test resoonse
            assert response.status_code == 201
            assert isinstance(response, requests.models.Response)
            assert isinstance(response.content, bytes)

            # Test warning
            assert len(warning) == 1
            assert issubclass(warning[-1].category, UserWarning)
            assert (
                "webhook_url not supplied, you will need to poll the statusUrl in order to get your result"
                in str(warning[-1].message)
            )


def test_post_request_unsuccessful_missing_api_secret():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )

    options = {
        "url": fake.url(),
        "webhook_url": f"{fake.url()}/webook",
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_client = UrlboxClient(api_key=api_key)

    with pytest.raises(Exception) as ex:
        urlbox_client.post(options)

    assert (
        "Missing api_secret when initialising client. Required for authorised post request."
        in str(ex.value)
    )


# Test generate_url
def test_generate_url_without_api_secret():
    api_key = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_client = UrlboxClient(api_key=api_key)

    urlbox_url = urlbox_client.generate_url(options)

    assert isinstance(urlbox_url, str)


def test_get_successful_as_str_with_api_secret():
    api_key = fake.pystr()
    api_secret = fake.pystr()

    format = random.choice(
        ["png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html"]
    )
    url = fake.url()

    options = {
        "url": url,
        "format": format,
        "full_page": random.choice([True, False]),
        "width": fake.random_int(),
    }

    urlbox_client = UrlboxClient(api_key=api_key, api_secret=api_secret)
    urlbox_url = urlbox_client.generate_url(options)

    assert isinstance(urlbox_url, str)
    # It doesn't leak the api_secret (uses the tokenised options instead)
    assert api_secret not in urlbox_url
