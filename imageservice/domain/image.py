import io
from typing import Union

import magic
from PIL import Image

from imageservice.services.s3 import S3

possible_mimetypes_extensions = {
    "JPG": ".jpg",
    "JPEG": ".jpeg",
    "PNG": ".png",
    "GIF": ".gif",
    "RIFF": ".webp",
}


class ImageDomain:
    def __init__(self, img_bytes):
        self.img_bytes = img_bytes
        self.image = Image.open(io.BytesIO(img_bytes))

    def resize(self, width, height) -> Image:
        return self.image.resize((width, height), Image.ANTIALIAS)

    @staticmethod
    def send_to_s3(image_name, bucket_path=None, public=True):
        """
        Resizes the image from formats allowed, and returns the info about s3 bucket path,
        and image's public url from each format
        :param image_name: str
        :param bucket_path: str
        :param public: bool
        :return:
        """
        return S3.send_resized_public_image(image_name, bucket_path, public)

    def discovery_mimetype(self) -> Union[str, None]:
        """
        This method will try to discover the mimetype for the image passed as bytes
        :return: str
        """
        mimetype = magic.from_buffer(self.img_bytes)

        for mimetype_starts in possible_mimetypes_extensions.keys():
            if mimetype.startswith(mimetype_starts):
                return mimetype_starts
        return None
