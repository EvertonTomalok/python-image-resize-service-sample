import os
import uuid
from dataclasses import dataclass
from typing import Union

from imageservice.domain.http import HTTP
from imageservice.domain.image import ImageDomain, possible_mimetypes_extensions


@dataclass
class ImageInfo:
    mimetype: str
    image_domain: ImageDomain


class ImageResizingUseCase:
    def __init__(self, img_url: str = None, img_bytes: bytes = None):
        """
            It'll resize an Image from an url or bytes received, and save it on s3 in different
        sizes.

        :param img_url: str
        :param img_bytes: bytes
        """
        self.img_url = img_url
        self.img_bytes = img_bytes
        self.formats = {
            "50x50": (50, 50),
            "250X250": (250, 250),
            "800x800": (800, 800),
        }

    def _retrieve_img(self) -> Union[ImageInfo, None]:
        if self.img_bytes:
            image_domain = ImageDomain(self.img_bytes)
            if mimetype_discovered := image_domain.discovery_mimetype():
                return ImageInfo(mimetype_discovered, image_domain)

        elif self.img_url:
            try:
                response = HTTP.download(self.img_url)
                if HTTP.page_content_is_image(response):
                    return ImageInfo(
                        HTTP.image_mimetype(response), ImageDomain(response.content)
                    )
            except Exception:
                return None

        return None

    def resize_and_save_on_s3(self, bucket_path: str = None) -> dict:
        image_info = self._retrieve_img()

        if not image_info:
            return {}

        img_extension = possible_mimetypes_extensions.get(image_info.mimetype.upper())
        objects_saved = dict()

        # If the IMAGE passed on constructor is valid, and we have a valid extension for this
        # image, so let's continue.
        if image_info and img_extension:
            unique_key = uuid.uuid1().hex

            for format_str, sizes in self.formats.items():
                width, height = sizes

                new_img = image_info.image_domain.resize(width, height)
                image_name = f"{unique_key}_{format_str}{img_extension}"

                new_img.save(image_name)

                # Sending image to s3
                obj_info = image_info.image_domain.send_to_s3(
                    image_name, bucket_path, public=True
                )

                # Insert on a dict all info about the images
                # resized and saved on s3
                objects_saved[format_str] = obj_info

                try:
                    os.remove(image_name)
                except Exception as error_removing:
                    print(error_removing)

        return objects_saved
