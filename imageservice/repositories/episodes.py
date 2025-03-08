from typing import List

from bson import ObjectId

from imageservice.adapters.mongodb import MongoDBDatabase

MATCH = {
    "$match": {
        "$expr": {"$ne": ["$itunes_image", "$last_itunes_image"]},
        "itunes_image": {"$ne": "N/A"},
        "$and": [
            # {
            #     "$or": [
            #         {"is_private": False},
            #         {"is_private": {"$exists": False}},
            #     ]
            # },
            {
                "$or": [
                    {"metadata.image_is_valid": True},
                    {"metadata.image_is_valid": {"$exists": False}},
                ]
            },
        ],
        "metadata.error": {"$exists": False},
        "lock": {"$exists": False},
    }
}

LOOK_UP = {
    "$lookup": {
        "from": "channels",
        "localField": "channel_id",
        "foreignField": "_id",
        "as": "channel",
    }
}

PROJECTION = {
    "$project": {
        "_id": 1,
        "title": 1,
        "itunes_image": 1,
        "last_itunes_image": 1,
        "channel.title": 1,
    }
}


class EpisodesRepository:
    @staticmethod
    def find_public_episodes_to_resize_image(max_documents: int = 100):
        """
        It returns a list like
        [{'_id': ObjectId('5eb5fd4ec6bf1b44480e7a08'),
          'channel': [{'title': 'Mundo Cristão Podcasts'}],
          'itunes_image': 'http://i1.sndcdn.com/artworks-000362275788-tx2aqo-t3000x3000.jpg',
          'title': 'Quarta Capa #11 - Cristãos e a Ciência, com Pedro Dulci'},
        ]
        :param max_documents: int
        :return: List[Dict]
        """
        with MongoDBDatabase("episodes") as db:
            return db.col.aggregate(
                [
                    MATCH,
                    LOOK_UP,
                    PROJECTION,
                    {"$limit": max_documents},
                ]
            )

    @staticmethod
    def count_public_episodes_to_resize_image():
        """
        It returns a document like
        [{'total_docs': 263396}]
        :return:
        """
        with MongoDBDatabase("episodes") as db:
            try:
                documents_array = list(
                    db.col.aggregate(
                        [
                            MATCH,
                            {"$count": "total_docs"},
                        ]
                    )
                )
                return documents_array[0].get("total_docs", 0)
            except Exception as err:
                print(err)
                return 0

    @staticmethod
    def update_itunes_image(
        _id: ObjectId,
        new_url: str,
        itunes_image_extra_images: dict = None,
        image_is_valid: bool = True,
    ):
        with MongoDBDatabase("episodes") as db:
            dict_to_set = {
                "last_itunes_image": new_url,
                "metadata": {"image_is_valid": image_is_valid},
            }
            if itunes_image_extra_images:
                dict_to_set["itunes_image_extra_images"] = itunes_image_extra_images
            db.col.update_one({"_id": _id}, {"$set": dict_to_set})

    @staticmethod
    def set_image_as_error(_id: ObjectId):
        with MongoDBDatabase("episodes") as db:
            db.col.update_one(
                {"_id": _id},
                {
                    "$set": {"metadata": {"error": True}},
                },
            )

    @staticmethod
    def set_image_as_invalid(_id: ObjectId):
        with MongoDBDatabase("episodes") as db:
            db.col.update_one(
                {"_id": _id},
                {
                    "$set": {"metadata": {"image_is_valid": False}},
                },
            )

    @staticmethod
    def set_lock_to_documents(_ids: List[ObjectId]):
        with MongoDBDatabase("episodes") as db:
            db.col.update_many({"_id": {"$in": _ids}}, {"$set": {"lock": True}})

    @staticmethod
    def unset_lock_to_documents(_ids: List[ObjectId]):
        with MongoDBDatabase("episodes") as db:
            db.col.update_many({"_id": {"$in": _ids}}, {"$unset": {"lock": ""}})

    @staticmethod
    def unset_lock_to_document(_id: ObjectId):
        with MongoDBDatabase("episodes") as db:
            db.col.update_one({"_id": _id}, {"$unset": {"lock": ""}})
