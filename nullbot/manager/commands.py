from nonebot import on_command, CommandSession
from nullbot.utils.deco import group_only, superuser_only
from nullbot.manager.mongo.db import DataManager


@on_command('init_db', only_to_me=False, shell_like=True)
@group_only
@superuser_only
async def handle_init_db(session: CommandSession):
    argv = session.args['argv']
    cleanup = True if '--clean' in argv else False
    
    msg = '正在初始化数据库...'
    if cleanup:
        msg += '(重置)'
    await session.send(msg)

    group_id = session.ctx['group_id']
    members = await session.bot.get_group_member_list(group_id=group_id)

    dm = DataManager(group_id)
    success = dm.init(members, cleanup)

    await session.send('成功导入{}位成员信息'.format(success))


@on_command('reset_db')
@group_only
@superuser_only
async def handle_reset_db(session: CommandSession):
    group_id = session.ctx['group_id']
    DataManager(group_id).reset()

    await session.send('数据库已重置')