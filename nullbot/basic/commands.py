from nonebot import on_command, CommandSession, get_bot
from nullbot.utils.helpers import *
from nonebot.permission import GROUP, GROUP_ADMIN, SUPERUSER
from spideroj.config import PLATFORM_URLS
import random


@on_command('ls', only_to_me=False, shell_like=True, permission=GROUP_ADMIN)
async def handle_ls(session: CommandSession):
    if not is_superuser(session):
        return
        
    group_id = session.ctx['group_id']
    user_id = session.ctx['user_id']

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
            await session.bot.send_msg(group_id=group_id, message=msg)

            if not ls_all:
                await session.bot.send_msg(group_id=group_id, message="Try `ls -a` or `ls --all` for full message.")
                break
    except Exception as e:
        print(type(e), e)


@on_command('notice', permission=SUPERUSER)
async def publish_notice(session: CommandSession):
    if not is_superuser(session):
        return

    if 'group_id' in session.ctx:
        return
    
    msg = session.current_arg

    data = await session.bot.get_group_list()
    for g in data:
        group_id = g['group_id']

        await session.bot.send_msg(group_id=group_id, message=msg)


@on_command('fake', permission=SUPERUSER)
async def fake_reply(session: CommandSession):
    if not is_superuser(session):
        return

    if 'group_id' in session.event:
        return

    msg = session.current_arg
    await session.bot.send_msg(group_id=598880963, message=msg)


@on_command('help', aliases='man', only_to_me=False, permission=GROUP, shell_like=True)
async def help(session: CommandSession):
    """help: 帮助

用法:
help [cmd]

示例:
help
help progress
"""
    group_id = session.ctx['group_id']

    argv = session.args['argv']

    commands = get_all_commands()
    lines = []
    try:
        if not argv:
            # global help
            at_str = "@闹闹 "
            for name, cmd in commands.items():
                if cmd.permission == GROUP:
                    docstr = cmd.func.__doc__
                    brief = docstr.split('\n')[0] if docstr else name

                    line = at_str if cmd.only_to_me else ""
                    line += brief
                    lines.append(line)
            
            random.shuffle(lines)
            lines = [get_random_header()] + lines
            for msg in multiline_msg_generator(lines=lines, lineno=False):
                await session.send(msg)

            return

        cmd = argv[0]
        usage = commands[cmd].func.__doc__
        
        if cmd == "register":
            # render docstring dynamically
            examples = [f"{oj}: {url.format('<id>')}" for oj, url in PLATFORM_URLS.items()]
            random.shuffle(examples)

            usage %= "\n".join(examples)

        lines += usage.split('\n')
        for msg in multiline_msg_generator(lines=lines, lineno=False):
            await session.send(msg)

    except Exception as e:
        print(e)
        await session.finish(f"命令{cmd}不存在或文档未定义！@Nuulll 甩锅")
    

@on_command('repo', only_to_me=False, permission=GROUP)
async def send_repo_info(session: CommandSession):
    """repo: 查看闹闹机器人开源仓库

用法:
repo
"""
    lines = [get_random_header()]

    lines += [
        'GITHUB: https://github.com/Nuullll/nullbot',
        '欢迎大家follow, star, watch三连'
    ]

    for msg in multiline_msg_generator(lines=lines, lineno=False):
        await session.send(msg)
    