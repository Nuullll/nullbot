import pymongo
from pymongo.errors import DuplicateKeyError
from spideroj.config import MEMBER_DB, OJID_DB, SNAPSHOT_DB
from spideroj.crawler.spiders import Spider
from datetime import timezone, datetime
from spideroj.crawler.model import Snapshot
from nullbot.utils.helpers import cst_dt_to_utc_ts


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

        member_set = {member['user_id'] for member in members}
        qq_list = self.get_all('qq_id', keep_inactive=True)
        
        for qq in qq_list:
            if qq not in member_set:
                self.members.update_one({
                    'qq_id': qq
                }, {
                    '$set': {
                        'is_active': False
                    }
                })
        
        success = 0
        for member in members:
            alias = member['card'] if member['card'] else member['nickname']
            success += self.upsert_member(qq_id=member['user_id'], group_alias=alias, join_time=member['join_time'])
        
        return success

    def get_all(self, field='qq_id', keep_inactive=False):
        docs = self.members.find({}, {field: 1, 'is_active': 1})

        if keep_inactive:
            return [doc[field] for doc in docs]

        result = []
        for doc in docs:
            if 'is_active' not in doc or doc['is_active']:
                result.append(doc[field])
        
        return result

    def upsert_member(self, qq_id, group_alias, join_time=0):
        try:
            self.members.update_one({
                'qq_id': qq_id
            }, {
                '$set': {
                    'group_alias': group_alias,
                    'join_time': join_time,
                    'is_active': True
                }
            }, upsert=True)
        except:
            return False

        return True

    def reset(self):
        self.members.drop()
        self.members = _member_db[self.group_id]

    def bind_account(self, qq_id, user_id, platform):
        try:
            res = _ids.insert_one({
                'platform': platform,
                'user_id': user_id,
                'qq_id': qq_id
            })
        except DuplicateKeyError:
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
        try:
            snapshots.insert_one({
                'timestamp': timestamp,
                'user_id': user_id,
                'platform': platform,
                'data': fields
            })
        except DuplicateKeyError:
            print("Warning: same timestamped data.")

        print(snapshots.find_one({'timestamp': timestamp}))

        snap = Snapshot(user_id, platform, timestamp, fields)

        return True, snap
    
    def load_latest_snapshot(self, qq_id, user_id, platform):
        
        snapshots = self.get_snapshots(qq_id)
        doc = snapshots.find_one({
            'user_id': user_id,
            'platform': platform
        }, sort=[('timestamp', -1)])

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

    def load_snapshot_around(self, qq_id, user_id, platform, cst_datetime):

        snapshots = self.get_snapshots(qq_id)
        reftime = cst_dt_to_utc_ts(cst_datetime)

        lb = snapshots.find_one({
            'timestamp': {
                '$lte': reftime
            },
            'user_id': user_id,
            'platform': platform
        }, sort=[('timestamp', -1)])

        ub = snapshots.find_one({
            'timestamp': {
                '$gt': reftime
            },
            'user_id': user_id,
            'platform': platform
        }, sort=[('timestamp', 1)])

        if not lb and not ub:
            raise FileNotFoundError("No snapshots.")

        pick = ''
        if lb and ub:
            if ub['timestamp'] - reftime < reftime - lb['timestamp']:
                pick = 'ub'
            else:
                pick = 'lb'
        else:
            if lb:
                pick = 'lb'
            else:
                pick = 'rb'

        doc = lb if pick == 'lb' else ub

        return Snapshot(**doc)
    
    def report_by_account(self, qq_id, user_id, platform, cst_starttime, cst_endtime, field='accepted'):
        
        start = self.load_snapshot_around(qq_id, user_id, platform, cst_starttime)
        end = self.load_snapshot_around(qq_id, user_id, platform, cst_endtime)

        vs = getattr(start, field)
        ve = getattr(end, field)

        return vs, ve

    def report_by_qq(self, qq_id, cst_starttime, cst_endtime, field='accepted'):

        accounts = self.query_binded_accounts(qq_id)

        vs, ve = 0, 0
        for user_id, platform in accounts:
            ds, de = self.report_by_account(qq_id, user_id, platform, cst_starttime, cst_endtime, field)

            vs += ds
            ve += de
        
        return vs, ve
    
    def report(self, cst_starttime, cst_endtime, field='accepted'):
        
        lines = []

        docs = self.members.find()

        for doc in docs:
            if 'is_active' in doc and not doc['is_active']:
                continue

            qq_id = doc['qq_id']
            alias = doc['group_alias']

            vs, ve = self.report_by_qq(qq_id, cst_starttime, cst_endtime, field)

            lines.append((alias, vs, ve))
        
        return lines

