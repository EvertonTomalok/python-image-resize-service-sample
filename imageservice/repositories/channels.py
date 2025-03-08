from bson import ObjectId

from imageservice.adapters.mongodb import MongoDBDatabase


class ChannelsRepository:
    @staticmethod
    def find_images_url_to_resize(
        max_documents: int = None, count_documents: bool = False
    ):
        with MongoDBDatabase("channels") as db:
            query = {
                "$and": [
                    {"image_url": {"$ne": "N/A"}},
                    {
                        "$or": [
                            {"$where": "this.image_url != this.last_image_url"},
                            {"$where": "this.itunes_image != this.last_itunes_image"},
                        ]
                    },
                    {
                        "$or": [
                            {"metadata.image_is_valid": True},
                            {"metadata.image_is_valid": {"$exists": False}},
                        ]
                    },
                    {"metadata.error": {"$exists": False}},
                ]
            }
            projection = {"image_url": 1, "itunes_image": 1, "title": 1}

            if count_documents:
                return db.col.find(query, projection).count()
            if max_documents:
                return db.col.find(query, projection).limit(max_documents)
            return db.col.find(query, projection)

    @staticmethod
    def find_channel_image_url_is_null_and_itunes_image_has_link():
        with MongoDBDatabase("channels") as db:
            query = {"image_url": {"$eq": "N/A"}, "itunes_image": {"$ne": "N/A"}}
            projection = {"image_url": 1, "itunes_image": 1}
            return db.col.find(query, projection)

    @staticmethod
    def update_image_url(
        _id: ObjectId, new_url: str, image_url_extra_images: dict = None
    ):
        with MongoDBDatabase("channels") as db:
            dict_to_set = {"image_url": new_url}
            if image_url_extra_images:
                dict_to_set["image_url_extra_images"] = image_url_extra_images

            db.col.update_one({"_id": _id}, {"$set": dict_to_set})

    @staticmethod
    def find_channel_itunes_image_is_null_and_image_url_has_link():
        with MongoDBDatabase("channels") as db:
            query = {"image_url": {"$ne": "N/A"}, "itunes_image": {"$eq": "N/A"}}
            projection = {"image_url": 1, "itunes_image": 1}
            return db.col.find(query, projection)

    @staticmethod
    def update_itunes_image(
        _id: ObjectId, new_url: str, itunes_image_extra_images: dict = None
    ):
        with MongoDBDatabase("channels") as db:
            dict_to_set = {"itunes_image": new_url}
            if itunes_image_extra_images:
                dict_to_set["itunes_image_extra_images"] = itunes_image_extra_images
            db.col.update_one({"_id": _id}, {"$set": dict_to_set})

    @staticmethod
    def update_extra_images(
        _id: ObjectId,
        last_image_url: str,
        last_itunes_image: str,
        image_url_extra_images: dict = None,
        itunes_image_extra_images: dict = None,
        image_is_valid: bool = True,
    ):
        with MongoDBDatabase("channels") as db:
            dict_to_set = {}
            if itunes_image_extra_images:
                dict_to_set["itunes_image_extra_images"] = itunes_image_extra_images
            if image_url_extra_images:
                dict_to_set["image_url_extra_images"] = image_url_extra_images

            if dict_to_set:
                dict_to_set["last_image_url"] = last_image_url
                dict_to_set["last_itunes_image"] = last_itunes_image
                dict_to_set["metadata"] = {"image_is_valid": image_is_valid}
                db.col.update_one({"_id": _id}, {"$set": dict_to_set})

    @staticmethod
    def set_image_as_error(_id: ObjectId):
        with MongoDBDatabase("channels") as db:
            db.col.update_one({"_id": _id}, {"$set": {"metadata": {"error": True}}})

    @staticmethod
    def set_image_as_invalid(_id: ObjectId):
        with MongoDBDatabase("channels") as db:
            db.col.update_one(
                {"_id": _id}, {"$set": {"metadata": {"image_is_valid": False}}}
            )
