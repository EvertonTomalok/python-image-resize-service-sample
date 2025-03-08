import sys
from datetime import datetime

from imageservice.repositories.episodes import EpisodesRepository
from imageservice.usecases.resize_img_url_and_itunes_image import (
    ResizingImageUrlAndItunesImage,
)


def main():
    batch = 100
    num_docs_processed = 0

    while documents := list(
        EpisodesRepository.find_public_episodes_to_resize_image(batch)
    ):
        _ids = [doc["_id"] for doc in documents]
        EpisodesRepository.set_lock_to_documents(_ids)
        try:
            for obj in documents:
                try:
                    if num_docs_processed % 10 == 0:
                        print(
                            f"[{datetime.now()}] - {num_docs_processed} was processed..."
                        )

                    num_docs_processed += 1
                    itunes_image = obj["itunes_image"]

                    channel_name = (
                        obj["channel"][0].get("title", "CUSTOM")
                        if len(obj["channel"]) > 0
                        else "CUSTOM"
                    )
                    info = ResizingImageUrlAndItunesImage.resize_image_and_return_info(
                        itunes_image=itunes_image, channel_name=channel_name
                    )

                    itunes_image_info_images_resized = info.get("itunes_image_info")
                    image_is_valid = itunes_image_info_images_resized is not None

                    if not image_is_valid:
                        EpisodesRepository.set_image_as_invalid(obj["_id"])
                    else:
                        EpisodesRepository.update_itunes_image(
                            obj["_id"],
                            obj["itunes_image"],
                            itunes_image_info_images_resized,
                        )

                    EpisodesRepository.unset_lock_to_document(obj["_id"])
                except Exception as err:
                    print(err)
                    EpisodesRepository.set_image_as_error(obj["_id"])
        except KeyboardInterrupt:
            print("Unlock documents and exiting...")
            EpisodesRepository.unset_lock_to_documents(_ids)
            sys.exit(0)
        except Exception as general_err:
            print(general_err)


if __name__ == "__main__":
    print(f"[{datetime.now()}] - starting ... \n")
    main()
    print(f"[{datetime.now()}] - ending ... \n")
