from nonebot import on_command, CommandSession, get_bot
import random
from nullbot.utils.helpers import multiline_msg_generator


@on_command('ls', only_to_me=False, shell_like=True)
async def handle_ls(session: CommandSession):
    
    # handle group message only
    if 'group_id' not in session.ctx:
        return
    
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']

    # permission check
    if not await is_owner_or_admin(group_id, user_id):
        await session.send('Permission denied.')
        return

    # args
    argv = session.args['argv']
    ls_all = True if '-a' in argv or '--all' in argv else False

    try:
        members = await session.bot.get_group_member_list(group_id=group_id)
    except Exception as e:
        print(type(e), e)
    
    lines = ['{} [{}]'.format(member['card'] if member['card'] else member['nickname'], member['user_id']) for member in members]
    
    count = len(lines)
    header = '正在获取群成员列表...共{}人'.format(count)
    try:
        await session.bot.send_msg(group_id=group_id, message=header)

        for msg in multiline_msg_generator(lines=lines, lineno=True):
            await session.bot.send_msg_rate_limited(group_id=group_id, message=msg)

            if not ls_all:
                await session.bot.send_msg(group_id=group_id, message="Try `ls -a` or `ls --all` for full message.")
                break
    except Exception as e:
        print(type(e), e)


async def is_owner_or_admin(group_id, user_id):
    bot = get_bot()

    data = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
    role = data.get('role', 'member')

    return role in ['owner', 'admin']


@on_command('tql', aliases=('666',), only_to_me=False)
async def repeat_tql(session: CommandSession):
    await session.send(session.ctx['message'])
