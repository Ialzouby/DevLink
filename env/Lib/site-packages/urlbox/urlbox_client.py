import json
import hmac
import requests
import urllib.parse
import validators
import warnings
from hashlib import sha1
from urlbox import InvalidUrlException


class UrlboxClient:
    """
        The core client object used to interact with the Urlbox API

        :param api_key: Your API key found in your Urlbox Dashboard
        `https://urlbox.io/dashboard/api`

        :param api_secret: (Optional) Your API secret found in your Urlbox
        Dashboard`https://urlbox.io/dashboard/api`
        Required for authenticated requests.
    """

    BASE_API_URL = "https://api.urlbox.io/v1/"
    POST_END_POINT = "render"

    def __init__(self, *, api_key, api_secret=None, api_host_name=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_api_url = self._init_base_api_url(api_host_name)

    def get(self, options):
        """
            Make simple get request to Urlbox API

            :param options: dictionary containing all of the options you want to set.
            eg: {"url": "http://example.com/", "format": "png", "full_page": True, "width": 300}

            format: can be either "png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html". Defaults to "png".

            Example: urlbox_client.get({"url": "http://example.com/", "format": "png", "full_page": True, "width": 300})
            API example: https://urlbox.io/docs/getting-started
            Full options reference: https://urlbox.io/docs/options
        """

        return requests.get(
            self.generate_url(options), allow_redirects=True, timeout=100
        )

    def delete(self, options):
        """
            Deletes the screenshot from the cache.

            :param options: dictionary containing url of the site the screneshot has captured
            and the format of the original screenshot eg: png, jpg, etc
            eg: {"url": "http://example.com/", "format": "png"}
        """

        processed_options, format = self._process_options(options)

        return requests.delete(
            (
                f"{self.base_api_url}"
                f"{self.api_key}/{format}"
                f"?{processed_options}"
            ),
            allow_redirects=True,
        )

    def head(self, options):
        """
            Make simple head request to Urlbox API

            To get the response status/headers without pulling down the full response body.

            :param options: dictionary containing all of the options you want to set.
            eg: {"url": "http://example.com/", "format": "png", "full_page": True, "width": 300}

            format: can be either "png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html". Defaults to "png".

            Example: urlbox_client.get({"url": "http://example.com/", "format": "png", "full_page": True, "width": 300})
            API example: https://urlbox.io/docs/getting-started
            Full options reference: https://urlbox.io/docs/options
        """

        processed_options, format = self._process_options(options)

        return requests.head(
            (
                f"{self.base_api_url}"
                f"{self.api_key}/{format}"
                f"?{processed_options}"
            ),
            allow_redirects=True,
            timeout=100,
        )

    def post(self, options):
        """
              Make post request to Urlbox API

              :param options: dictionary containing all of the options you want to set.
              eg: {"url": "http://example.com/", "webhook_url": "http://yoursite.com/webhook", "format": "png", "full_page": True, "width": 300}

              format: can be either "png", "jpg", "jpeg", "avif", "webp", "pdf", "svg", "html". Defaults to "png".

              Example: urlbox_client.post({"url": "http://example.com/", "webhook_url": "http://yoursite.com/webhook", "format": "png", "full_page": True, "width": 300})
              Full options reference: https://urlbox.io/docs/options
          """

        if "webhook_url" not in options:
            warnings.warn(
                "webhook_url not supplied, you will need to poll the statusUrl in order to get your result"
            )

        if self.api_secret is None:
            raise Exception(
                "Missing api_secret when initialising client. Required for authorised post request."
            )

        processed_options, _ = self._process_options_post_request(options)

        return requests.post(
            f"{self.base_api_url}{self.POST_END_POINT}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_secret}",
            },
            allow_redirects=True,
            json=processed_options,
            timeout=5,
        )

    def generate_url(self, options):
        """
            Generate the Urlbox URL as a string for use directly in HTML templates, the browser etc.

            :param options: dictionary containing all of the options you want to set.
            eg: {"url": "http://example.com/", "format": "png", "full_page": True, "width": 300}

            Example:
            In your python_code.py:
            # Initialise the UrlboxClient (YOUR_API_SECRET is optional but recommended)
            urlbox_client = UrlboxClient(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")

            screenshot_url = urlbox_client.generate_url({"url": "http://example.com/"})

            In your html template:
            <img src="{{  screenshot_url }}"/>

            Full options reference: https://urlbox.io/docs/options
        """

        processed_options, format = self._process_options(options)

        if self.api_secret is None:
            return (
                f"{self.base_api_url}"
                f"{self.api_key}/{format}"
                f"?{processed_options}"
            )
        else:
            return (
                f"{self.base_api_url}"
                f"{self.api_key}/{self._token(processed_options)}/{format}"
                f"?{processed_options}"
            )

    # private

    def _init_base_api_url(self, api_host_name):
        if api_host_name is None:
            return self.BASE_API_URL
        else:
            return f"https://{api_host_name}/"

    def _prepend_schema(self, url):
        if not url.startswith("http"):
            return f"http://{url}"
        else:
            return url

    def _process_options(self, options, url_encode_options=True):
        self._raise_key_error_if_missing_required_keys(options)

        processed_options = options.copy()

        if "url" in processed_options:
            processed_options["url"] = self._process_url(
                processed_options["url"]
            )

        format = processed_options.get("format", "png")
        processed_options["format"] = format

        if url_encode_options:
            return (
                urllib.parse.urlencode(processed_options, doseq=True),
                format,
            )
        else:
            return processed_options, format

    def _process_options_post_request(self, options):
        return self._process_options(options, False)

    def _process_url(self, url):
        url_stripped = url.strip()
        url_parsed = self._prepend_schema(url_stripped)

        if not validators.url(url_parsed) == True:
            raise InvalidUrlException(url_parsed)

        return url_parsed

    def _raise_key_error_if_missing_required_keys(self, options):
        if "html" not in options and "url" not in options:
            raise KeyError("Missing 'url' or 'html' key in options")

    def _token(self, url_encoded_options):
        return (
            hmac.new(
                str.encode(self.api_secret),
                str.encode(url_encoded_options),
                sha1,
            )
            .hexdigest()
            .rstrip("\n")
        )
