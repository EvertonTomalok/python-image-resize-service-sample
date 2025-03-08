import logging
import os
import warnings

import requests.exceptions
from requests_html import HTMLSession

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

logging.basicConfig(format="[%(levelname)s] [%(name)s] %(asctime)-15s  -> %(message)s")
LOGGER = logging.getLogger("HTTP")

if os.environ.get("LEVEL", "DEBUG") == "DEBUG":
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)


class HTTP:
    @staticmethod
    def send_postback(url: str, body: dict):
        with HTMLSession() as session:
            try:
                session.post(url, json=body, timeout=5)
                return True
            except Exception as err_post_back:
                LOGGER.error(err_post_back)
                return False

    @staticmethod
    def download(img_url: str):
        with HTMLSession() as session:
            for i in range(3):
                try:
                    return session.get(
                        img_url,
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                " Chrome/89.0.4389.114 Safari/537.36"
                            )
                        },
                        timeout=12,
                        verify=False,
                    )
                except Exception:
                    continue
            raise requests.exceptions.ConnectionError()

    @staticmethod
    def page_content_is_image(response):
        if hasattr(response, "headers"):
            identify, image_type = response.headers.get("Content-Type", "").split("/")
            return identify.lower() == "image"
        return False

    @staticmethod
    def image_mimetype(response):
        if hasattr(response, "headers"):
            _, image_type = response.headers.get("Content-Type", "").split("/")
            return image_type
        return None
