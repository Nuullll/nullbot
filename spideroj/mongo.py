import pymongo
from spideroj.config import MONGODB_NAME, ID_CHECK_DB
from spideroj.crawler.spiders import Spider
from datetime import timezone, datetime


_client = pymongo.MongoClient()
_db = _client[MONGODB_NAME]
_id_collection = _db[ID_CHECK_DB]
_id_collection.create_index([('platform', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True, background=True)


class DataManager(object):
    
    def __init__(self, group_id):
        self.group_id = str(group_id)
        self.collection = _db[self.group_id]
    
    @staticmethod
    def get_profile(platform, user_id):
        spider = Spider.get_spider(platform)
        ok, data = spider.get_user_data(user_id)
        
        return ok, data
    
    @staticmethod
    def utc_now():
        return int(datetime.now(tz=timezone.utc).timestamp())

    def init(self, members, cleanup=False):
        if cleanup:
            self.reset()

        self.collection.create_index('qq_id', unique=True, background=True)

        success = 0
        for member in members:
            alias = member['card'] if member['card'] else member['nickname']
            success += self.upsert_member(qq_id=member['user_id'], group_alias=alias, join_time=member['join_time'])
        
        return success

    def upsert_member(self, qq_id, group_alias, join_time=0):
        try:
            self.collection.update_one({
                'qq_id': qq_id
            }, {
                '$set': {
                    'group_alias': group_alias,
                    'join_time': join_time
                }
            }, upsert=True)
        except:
            return False

        return True

    def reset(self):
        self.collection.drop()
        self.collection = _db[self.group_id]
    
    def bind_account(self, qq_id, user_id, platform):
        res = _id_collection.insert_one({
            'platform': platform,
            'user_id': user_id,
            'qq_id': qq_id
        })

        if not res:
            return False
        
        return True
    
    def unbind_account(self, qq_id, user_id, platform):
        _id_collection.delete_one({
            'platform': platform,
            'user_id': user_id,
            'qq_id': qq_id
        })

    def is_account_binded(self, user_id, platform):
        doc = _id_collection.find_one({
            'platform': platform,
            'user_id': user_id
        })

        if doc:
            return True, doc['qq_id']
        
        return False, 0
    
    def query_binded_accounts(self, qq_id):
        docs = _id_collection.find({
            'qq_id': qq_id
        })

        res = []
        for doc in docs:
            res.append((doc['user_id'], doc['platform']))
        
        return res

    def remove_account(self, qq_id, user_id, platform):
        self.collection.update_one({
            'qq_id': qq_id
        }, {
            '$unset': {
                'accounts.{user_id}@{platform}': ''
            }
        })

        self.unbind_account(qq_id, user_id, platform)

    def get_and_save_user_summary(self, qq_id, user_id, platform):
        ok, fields = self.get_profile(platform, user_id)

        if not ok:
            return False
        
        self.collection.update_one({
            'qq_id': qq_id
        }, {
            '$set': {
                f'accounts.{user_id}@{platform}.{self.utc_now()}': {
                    **fields
                }
            }
        }, upsert=True)

        print(self.collection.find_one({'qq_id': qq_id}))

        return True