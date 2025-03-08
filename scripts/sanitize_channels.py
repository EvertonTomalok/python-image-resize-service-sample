from tqdm import tqdm

from imageservice.repositories.channels import ChannelsRepository


def sanitize_image_url():
    list_object = list(
        ChannelsRepository.find_channel_image_url_is_null_and_itunes_image_has_link()
    )
    if len_docs := len(list_object):
        with tqdm(total=len_docs) as pbar:
            for obj in list_object:
                ChannelsRepository.update_image_url(obj["_id"], obj["itunes_image"])
                pbar.update(1)


def sanitize_itunes_image():
    list_object = list(
        ChannelsRepository.find_channel_itunes_image_is_null_and_image_url_has_link()
    )

    if len_docs := len(list_object):
        with tqdm(total=len_docs) as pbar:
            for obj in list_object:
                ChannelsRepository.update_itunes_image(obj["_id"], obj["image_url"])
                pbar.update(1)


if __name__ == "__main__":
    sanitize_image_url()
    sanitize_itunes_image()
