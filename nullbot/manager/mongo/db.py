from pymongo import MongoClient
from nullbot.config import MONGODB_NAME


_client = MongoClient()
_db = _client[MONGODB_NAME]


class DataManager(object):

    def __init__(self, group_id):
        self.group_id = str(group_id)
        self.collection = _db[self.group_id]
    
    def init(self, members, cleanup=False):
        if cleanup:
            self.reset()

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
        