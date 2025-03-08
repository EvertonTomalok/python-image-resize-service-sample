from imageservice.usecases.imageresizing import ImageResizingUseCase


class ResizingImageUrlAndItunesImage:
    @staticmethod
    def resize_image_and_return_info(
        image_url: str = None, itunes_image: str = None, channel_name: str = None
    ):
        # If the both url are the same, we'll process once and attribute the url generated
        # for both fields
        if image_url == itunes_image and image_url != "N/A" and itunes_image != "N/A":
            images_resized_obj = ImageResizingUseCase(image_url).resize_and_save_on_s3(
                bucket_path=channel_name
            )

            return {
                "image_url_info": images_resized_obj or None,
                "itunes_image_info": images_resized_obj or None,
            }

        # Check if has a valid url for each field
        resized_images_info = {}
        if image_url and image_url != "N/A":
            img_url_obj = ImageResizingUseCase(image_url).resize_and_save_on_s3(
                bucket_path=channel_name
            )
            resized_images_info["image_url_info"] = img_url_obj or None

        if itunes_image and itunes_image != "N/A":
            itunes_image_obj = ImageResizingUseCase(itunes_image).resize_and_save_on_s3(
                bucket_path=channel_name
            )
            resized_images_info["itunes_image_info"] = itunes_image_obj or None

        return resized_images_info
