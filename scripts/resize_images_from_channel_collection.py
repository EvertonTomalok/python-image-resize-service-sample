from datetime import datetime

from tqdm import tqdm

from imageservice.repositories.channels import ChannelsRepository
from imageservice.usecases.resize_img_url_and_itunes_image import (
    ResizingImageUrlAndItunesImage,
)


def main():
    count_documents_to_handle = ChannelsRepository.find_images_url_to_resize(
        count_documents=True
    )
    if count_documents_to_handle > 0:
        with tqdm(total=count_documents_to_handle) as pbar:
            while documents := list(ChannelsRepository.find_images_url_to_resize(100)):
                for obj in documents:
                    try:
                        info = (
                            ResizingImageUrlAndItunesImage.resize_image_and_return_info(
                                obj["image_url"], obj["itunes_image"], obj["title"]
                            )
                        )

                        image_url_info_images_resized = info.get("image_url_info")
                        itunes_image_info_images_resized = info.get("image_url_info")

                        image_is_valid = (
                            image_url_info_images_resized is not None
                            or itunes_image_info_images_resized is not None
                        )

                        if not image_is_valid:
                            ChannelsRepository.set_image_as_invalid(obj["_id"])
                        else:
                            ChannelsRepository.update_extra_images(
                                obj["_id"],
                                obj["image_url"],
                                obj["itunes_image"],
                                info.get("image_url_info"),
                                info.get("itunes_image_info"),
                                image_is_valid,
                            )
                    except Exception:
                        ChannelsRepository.set_image_as_error(obj["_id"])

                    pbar.update(1)


if __name__ == "__main__":
    print(
        f"[{datetime.now()}] Starting script -> 'image-service-resizing-images-from-channel-collection' ..."
    )
    main()
    print(
        f"[{datetime.now()}] Finishing script -> 'image-service-resizing-images-from-channel-collection' ..."
    )
