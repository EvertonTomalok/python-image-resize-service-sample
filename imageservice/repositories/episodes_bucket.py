from imageservice.adapters.mongodb import MongoDBDatabase


class EpisodesBucket:
    @staticmethod
    def find_bucket_images_resized_by_image_url(image_url: str):
        with MongoDBDatabase("episodes_bucket") as db:
            return db.col.find_one({"image_url": image_url})

    @staticmethod
    def insert_bucket_images(image_url: str, itunes_image_info: dict):
        with MongoDBDatabase("episodes_bucket") as db:
            db.col.insert_one(
                {"image_url": image_url, "itunes_image_info": itunes_image_info}
            )
