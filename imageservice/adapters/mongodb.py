from logging import INFO, getLogger
from os import getenv

from pymongo import ASCENDING, MongoClient, ReturnDocument

DB_ENVIRONMENT = getenv("DB_ENVIRONMENT", "DEVELOP")
DATABASE_NAME = "dbkube-dev" if DB_ENVIRONMENT.upper() == "DEVELOP" else "dbkube-prod"

MONGODB_SETTINGS = {
    "url": getenv(
        "MONGO_URL",
        f"mongodb+srv://UserKube:cWsbTvfi0ffrItV5@clusterkubemongo-l5ehh.mongodb.net/{DATABASE_NAME}",
    )
}

logger = getLogger()
logger.setLevel(INFO)


class MongoDBDatabase:
    __client = None
    __database = None
    __database_name = None

    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.database_name = DATABASE_NAME
        self.__setup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__teardown()

    def __del__(self):
        self.__teardown()

    def __setup(self):
        if not self.__client:
            self.__client = MongoClient(MONGODB_SETTINGS["url"])
        self.__database = self.__client[self.database_name]
        self.col = self.__database[self.collection_name]

    def __teardown(self):
        if self.__client:
            try:
                self.__client.close()
            except TypeError:
                pass

    def insert_update(self, data: dict, filter_to_update: dict):
        filter_to_update = filter_to_update

        self.col.update_one(
            filter_to_update,
            {"$set": data},
            upsert=True,
        )

    def find_one_and_update(self, filter: dict, update: dict):
        return self.col.find_one_and_update(
            filter, update, return_document=ReturnDocument.AFTER
        )

    def create_index_episodes_match(self):
        self.__database["episodes"].create_index(
            [
                ("itunes_image", ASCENDING),
                ("last_itunes_image", ASCENDING),
                ("is_private", ASCENDING),
                ("metadata.image_is_valid", ASCENDING),
                ("metadata.error", ASCENDING),
                ("lock", ASCENDING),
            ],
            background=True,
        )
