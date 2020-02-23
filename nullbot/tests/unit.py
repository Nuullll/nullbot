from nonebot import get_bot, on_command, on_request, on_notice, CommandSession, RequestSession, NoticeSession
from nonebot.permission import PRIVATE, SUPERUSER
from spideroj.mongo import DataManager
from nullbot.utils.helpers import multiline_msg_generator


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


@on_command('do_db_refactor', permission=SUPERUSER)
async def do_db_refactor(session: CommandSession):
    group_id = 1234

    dm = DataManager(group_id)

    for doc in dm.collection.find({}):
        qq_id = doc['qq_id']
        if 'accounts' not in doc or len(doc['accounts']) == 0:
            continue
        
        for key, data in doc['accounts'].items():
            
            for timestamp, fields in data.items():
                dm.collection.update_one({
                    'qq_id': qq_id
                }, {
                    '$push': {
                        f"accounts.{key}.snapshots": {
                            "timestamp": int(timestamp),
                            "data": fields
                        }
                    }, 
                    '$unset': {
                        f"accounts.{key}.{timestamp}": ""
                    }
                })

    for doc in dm.collection.find({}):
        print(doc)
    