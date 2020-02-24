from nonebot import get_bot, on_command, on_request, on_notice, CommandSession, RequestSession, NoticeSession
from nonebot.permission import PRIVATE, SUPERUSER
from spideroj.mongo import DataManager
from nullbot.utils.helpers import multiline_msg_generator
import asyncio
from spideroj.config import OJID_DB, MEMBER_DB, SNAPSHOT_DB
import pymongo


QQ_ID = 724463877
GROUP_ID_200 = 598880963
GROUP_ID_WEEKLY = 958127821


async def tell_dad(msg):
    bot = get_bot()
    await bot.send_private_msg_rate_limited(user_id=QQ_ID, message=msg)


@on_command('test_send_private_msg', aliases=('私聊测试', ), permission=SUPERUSER)
async def test_send_private_msg(session: CommandSession):
    await tell_dad('测试成功')


@on_command('test_at', permission=SUPERUSER)
async def test_at(session: CommandSession):
    await tell_dad('欢迎[CQ:at,qq={}]'.format(QQ_ID))
    

@on_command('test_db_refactor', permission=SUPERUSER)
async def test_db_refactor(session: CommandSession):
    group_id = 1234

    dm = DataManager(group_id)
    
    ok, snapshot = await dm.get_and_save_user_summary(QQ_ID, 'nuullll', 'leetcode')
    await session.send(str(snapshot.accepted))


@on_command('show_db', permission=SUPERUSER)
async def show_db(session: CommandSession):
    db = pymongo.MongoClient()[SNAPSHOT_DB]
    target = db['724463877']

    docs = target.find()
    for doc in docs:
        print(doc)
    
    print(docs.count())

@on_command('test_timer', permission=SUPERUSER)
async def test_timer(session: CommandSession):
    async def timer():
        for count in range(10):
            print(count)
            await asyncio.sleep(1)
            
    task = asyncio.create_task(timer())


@on_command('refactor_snapshots', permission=SUPERUSER)
async def refactor_ids(session: CommandSession):
    src = pymongo.MongoClient()[MEMBER_DB]
    dst = pymongo.MongoClient()[SNAPSHOT_DB]

    for group_id in [GROUP_ID_WEEKLY, GROUP_ID_200]:
        collection = src[str(group_id)]

        for doc in collection.find({}):
            qq_id = doc['qq_id']
            accounts = doc['accounts']
            for key, value in accounts.items():
                user_id, platform = key.split('@')

                for snapshot in value['snapshots']:
                    timestamp = snapshot['timestamp']
                    data = snapshot['data']

                    target = dst[str(qq_id)]
                    try:
                        target.insert_one({
                            'timestamp': timestamp,
                            'user_id': user_id,
                            'platform': platform,
                            'data': data
                        })
                    except Exception as e:
                        print(e)


@on_command('drop_db', permission=SUPERUSER)
async def drop_db(session: CommandSession):
    db = pymongo.MongoClient()[OJID_DB]

    for group_id in [GROUP_ID_200, GROUP_ID_WEEKLY]:
        db[str(group_id)].drop()
