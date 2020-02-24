import pymongo
from spideroj.config import MEMBER_DB, OJID_DB, SNAPSHOT_DB
from spideroj.crawler.spiders import Spider
from datetime import timezone, datetime
from spideroj.crawler.model import Snapshot


_client = pymongo.MongoClient()
_member_db = _client[MEMBER_DB]
_ids = _client[OJID_DB]['all']
_ids.create_index([('platform', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True, background=True)
_snapshot_db = _client[SNAPSHOT_DB]


class DataManager(object):
    
    def __init__(self, group_id):
        self.group_id = str(group_id)
        self.members = _member_db[self.group_id]
    
    @staticmethod
    async def get_profile(platform, user_id):
        spider = Spider.get_spider(platform)
        ok, data = await spider.get_user_data(user_id)
        
        return ok, data
    
    @staticmethod
    def utc_now():
        return int(datetime.utcnow().timestamp())

    @staticmethod
    def get_snapshots(qq_id):
        snapshots = _snapshot_db[str(qq_id)]
        snapshots.create_index([('timestamp', pymongo.DESCENDING), ('platform', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True, background=True)
        return snapshots

    def init(self, members, cleanup=False):
        if cleanup:
            self.reset()

        self.members.create_index('qq_id', unique=True, background=True)

        success = 0
        for member in members:
            alias = member['card'] if member['card'] else member['nickname']
            success += self.upsert_member(qq_id=member['user_id'], group_alias=alias, join_time=member['join_time'])
        
        return success

    def upsert_member(self, qq_id, group_alias, join_time=0):
        try:
            self.members.update_one({
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
        self.members.drop()
        self.members = _member_db[self.group_id]

    def bind_account(self, qq_id, user_id, platform):
        res = _ids.insert_one({
            'platform': platform,
            'user_id': user_id,
            'qq_id': qq_id
        })

        if not res:
            return False
        
        return True
    
    def unbind_account(self, qq_id, user_id, platform):
        _ids.delete_one({
            'platform': platform,
            'user_id': user_id,
            'qq_id': qq_id
        })

    def is_account_binded(self, user_id, platform):
        doc = _ids.find_one({
            'platform': platform,
            'user_id': user_id
        })

        if doc:
            return True, doc['qq_id']
        
        return False, 0
    
    def query_binded_accounts(self, qq_id):
        docs = _ids.find({
            'qq_id': qq_id
        })

        res = []
        for doc in docs:
            res.append((doc['user_id'], doc['platform']))
        
        return res

    def remove_account(self, qq_id, user_id, platform):
        self.unbind_account(qq_id, user_id, platform)

    async def get_and_save_user_summary(self, qq_id, user_id, platform):
        ok, fields = await self.get_profile(platform, user_id)

        if not ok:
            return False, None

        timestamp = self.utc_now()

        snapshots = self.get_snapshots(qq_id)
        snapshots.insert_one({
            'timestamp': timestamp,
            'user_id': user_id,
            'platform': platform,
            'data': fields
        })

        print(snapshots.find_one({'timestamp': timestamp}))

        snap = Snapshot(user_id, platform, timestamp, fields)

        return True, snap
    
    def load_latest_snapshot(self, qq_id, user_id, platform):
        
        snapshots = self.get_snapshots(qq_id)
        doc = snapshots.find_one({
            'user_id': user_id,
            'platform': platform
        })

        snapshot = Snapshot(**doc)

        return snapshot
    
    async def get_and_save_all_user_summary(self):
        qqs = []
        
        for doc in self.members.find({}):
            qqs.append(doc['qq_id'])
        
        fails = []
        
        for qq_id in qqs:
            accounts = self.query_binded_accounts(qq_id)

            for user_id, platform in accounts:
                ok, fields = await self.get_and_save_user_summary(qq_id, user_id, platform)

                if not ok:
                    fails.append((qq_id, user_id, platform))

        return fails