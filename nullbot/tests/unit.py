from nonebot import get_bot, on_command, on_request, on_notice, CommandSession, RequestSession, NoticeSession
from spideroj.mongo import DataManager
from nullbot.utils.deco import superuser_only
from nullbot.utils.helpers import multiline_msg_generator


QQ_ID = 724463877
GROUP_ID = 598880963
GROUP_ID = 958127821


async def tell_dad(msg):
    bot = get_bot()
    await bot.send_private_msg_rate_limited(user_id=QQ_ID, message=msg)


@on_command('test_send_private_msg', aliases=('私聊测试', ))
@superuser_only
async def test_send_private_msg(session: CommandSession):
    await tell_dad('测试成功')


@on_command('test_at')
@superuser_only
async def test_at(session: CommandSession):
    await tell_dad('欢迎[CQ:at,qq={}]'.format(QQ_ID))


@on_command('test_upsert_member')
@superuser_only
async def test_upsert_member(session: CommandSession):
    test_group_id = 1234
    dm = DataManager(test_group_id)
    dm.reset()

    dm.upsert_member(qq_id=QQ_ID, group_alias='Nuullll', join_time=128888)

    msg = dm.collection.find_one_and_delete({
        'qq_id': QQ_ID
    }).__repr__()

    await tell_dad(message=msg)


@on_command('test_upsert_members')
@superuser_only
async def test_upsert_members(session: CommandSession):
    test_group_id = 1234
    dm = DataManager(test_group_id)
    dm.reset()
    
    members = await session.bot.get_group_member_list(group_id=GROUP_ID)

    for member in members:
        alias = member['card'] if member['card'] else member['nickname']
        dm.upsert_member(member['user_id'], alias, member['join_time'])
    
    docs = dm.collection.find({})
    await tell_dad('Found {} documents.'.format(docs.count()))

    lines = [doc.__repr__() for doc in docs]
    for msg in multiline_msg_generator(lines=lines, lineno=True):
        await tell_dad(msg)
    