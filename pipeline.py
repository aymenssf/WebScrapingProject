import pymongo
from pymongo.server_api import ServerApi


class VariantsPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        MONGO_USER = settings.get('MONGO_USER')
        MONGO_PASS = settings.get('MONGO_PASS')
        # MONGO_HOST = settings.get('MONGO_HOST')
        # MONGO_PORT = settings.get('MONGO_PORT')
        MONGO_DB = settings.get('MONGO_DB')
        AUTH = settings.get('AUTH')
        return cls(
            MONGO_USER,
            MONGO_PASS,
            MONGO_DB,
        )

    def __init__(self, MONGO_USER, MONGO_PASS, MONGO_DB):
        mongo_uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.mudw6.mongodb.net/{MONGO_DB}?retryWrites=true" \
                    f"&w=majority "
        self.client = pymongo.MongoClient(
            mongo_uri,
            server_api=ServerApi('1')
        )
        self.db = self.client[MONGO_DB]

    def process_item(self, item, spider):
        self.db['collection_lin1'].insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
