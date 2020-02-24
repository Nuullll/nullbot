from nonebot import get_bot, on_command, on_request, on_notice, CommandSession, RequestSession, NoticeSession
from nonebot.permission import PRIVATE, SUPERUSER
from spideroj.mongo import DataManager
from nullbot.utils.helpers import multiline_msg_generator
import asyncio
from spideroj.config import OJID_DB
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
    db = pymongo.MongoClient()[OJID_DB]
    target = db['all']

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


@on_command('refactor_ids', permission=SUPERUSER)
async def refactor_ids(session: CommandSession):
    db = pymongo.MongoClient()[OJID_DB]
    target = db['all']

    for group_id in [GROUP_ID_WEEKLY, GROUP_ID_200]:
        collection = db[str(group_id)]

        for doc in collection.find({}):
            target.insert_one(doc)
