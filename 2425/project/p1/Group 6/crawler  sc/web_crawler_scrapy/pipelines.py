# myproject/pipelines.py
import pymongo
from scrapy.exceptions import DropItem

class MongoDBPipeline:

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(spider.settings.get('MONGODB_URI'))
        self.db = self.client[spider.settings.get('MONGODB_DB')]
        self.collection = self.db[spider.settings.get('MONGODB_COLLECTION')]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if item:
            self.collection.insert_one(dict(item))
            return item
        else:
            raise DropItem("Missing item")