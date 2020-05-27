import nonebot
from nonebot import on_command, CommandSession
from nonebot.permission import GROUP, GROUP_ADMIN, SUPERUSER
from nullbot.config import REPORT_TOTAL_MAX_ENTRIES
from nullbot.utils.helpers import parse_cq_at
from spideroj.config import PLATFORM_URLS, USER_UPDATE_COOLDOWN
from spideroj.mongo import DataManager
import re
from random import shuffle
from nullbot.utils.helpers import multiline_msg_generator, last_sunday, autoalign, cstnow, long_long_ago
from datetime import datetime
from operator import itemgetter
from nonebot.command import call_command


@on_command('init_db', only_to_me=False, shell_like=True, permission=SUPERUSER)
async def handle_init_db(session: CommandSession):
    argv = session.args['argv']
    cleanup = True if '-c' in argv else False
    
    msg = '正在初始化数据库...'
    if cleanup:
        msg += '(重置)'
    await session.send(msg)

    group_id = session.ctx['group_id']
    members = await session.bot.get_group_member_list(group_id=group_id)

    dm = DataManager(group_id)
    success = dm.init(members, cleanup)

    await session.send('成功导入{}位成员信息'.format(success))


@on_command('reset_db', permission=SUPERUSER)
async def handle_reset_db(session: CommandSession):
    group_id = session.ctx['group_id']
    DataManager(group_id).reset()

    await session.send('数据库已重置')


@on_command('register', only_to_me=False, permission=GROUP)
async def handle_register(session: CommandSession):
    """register: 绑定OJ账号

用法:
register <your OJ profile url>

目前支持的OJ平台:
%s

示例:
register https://leetcode.com/nuullll
"""
    await register_helper(session)


@on_command('unregister', aliases=('deregister',), only_to_me=False, shell_like=True, permission=GROUP)
async def handle_unregister(session: CommandSession):
    """unregister: 解绑账号

用法: 
unregister [-a] [platform] [user_id]

可选参数:
-a 解绑本人所有OJ平台账号

示例:
unregister -a
unregister leetcodecn nuullll
"""
    USAGE = handle_unregister.__doc__

    # args
    argv = session.args['argv']
    if not argv:
        await session.finish(USAGE)
        return

    rm_all = True if '-a' in argv else False

    group_id = session.ctx['group_id']
    qq_id = session.ctx['user_id']

    dm = DataManager(group_id)
    if rm_all:
        candidates = dm.query_binded_accounts(qq_id)
    else:
        try:
            platform = argv[0]
            user_id = argv[1]
        except:
            await session.send("参数有误！")
            await session.finish(USAGE)
            return
        
        binded, bind_qq = dm.is_account_binded(user_id, platform)
        if not binded or bind_qq != qq_id:
            await session.finish("账号不存在，解绑失败。@我 accounts 查询已绑定账号。")
            return
        
        candidates = [(user_id, platform)]
    
    for u, p in candidates:
        dm.remove_account(qq_id, u, p)
    
    await session.finish("解绑成功。")


@on_command('accounts', aliases='account', only_to_me=False, permission=GROUP)
async def handle_accounts(session: CommandSession):
    """accounts: 查询当前已绑定账号

用法:
accounts
"""
    group_id = session.ctx['group_id']
    qq_id = session.ctx['user_id']

    dm = DataManager(group_id)
    accounts = dm.query_binded_accounts(qq_id)

    if accounts:
        msg = '已绑定账号：\n' + '\n'.join([u+'@'+p for u, p in accounts])
    else:
        msg = '并没有绑定账号。'
    
    await session.send(msg, at_sender=True)


@on_command('register_for', only_to_me=False, shell_like=True, permission=SUPERUSER)
async def handle_register_for(session: CommandSession):
    await register_helper(session, for_other=True)


async def register_helper(session, for_other=False):

    examples = [f"{oj}: {url.format('<id>')}" for oj, url in PLATFORM_URLS.items()]
    shuffle(examples)

    USAGE = """
用法:
register <your OJ profile url>

目前支持的OJ平台:
""" + "\n".join(examples) + """

示例:
register https://leetcode.com/nuullll
"""

    group_id = session.ctx['group_id']

    if not for_other:
        url = session.current_arg_text.strip()

        if not url:
            await session.finish("未检测到url\n" + USAGE)
            return
        
        url = url.split()[0]
        
        qq_id = session.ctx['user_id']
    else:
        argv = session.args['argv']
        qq_id, url = argv

        try:
            if qq_id.isnumeric():
                qq_id = int(qq_id)
            else:
                # infer CQ code
                qq_id = parse_cq_at(qq_id)
        except:
            await session.finish('参数错误！')
            return
    
    platform = ''
    user_id = ''
    for oj, template in PLATFORM_URLS.items():
        # escape special character in template
        template = template.replace('?', '\?')
        m = re.search(template.format('([a-zA-Z0-9_-]+)'), url)
        if m:
            platform = oj
            user_id = m.group(1)
            break
    
    if not user_id:
        await session.finish("请检查URL格式\n" + USAGE)
        return

    dm = DataManager(group_id)

    binded, bind_qq = dm.is_account_binded(user_id, platform)
    if binded:
        if bind_qq == qq_id:
            await session.finish(f"您已绑定{user_id}@{platform}，请勿重复操作。")
        else:
            await session.finish(f"绑定失败，{user_id}@{platform}已被用户[CQ:at,qq={bind_qq}]绑定！")
        return

    ok, snapshot = await dm.get_and_save_user_summary(qq_id, user_id, platform)

    if not ok:
        await session.send("ID错误或网络错误！请检查后重试。")
        return
    
    if not dm.bind_account(qq_id, user_id, platform):
        await session.finish("绑定失败，代码线程不安全。")
        return

    await session.send(f"{user_id}@{platform}绑定成功！")
    for msg in multiline_msg_generator(snapshot.lines):
        await session.send(msg)


@on_command('registered', only_to_me=False, shell_like=True, permission=GROUP_ADMIN)
async def query_registered(session: CommandSession):
    argv = session.args['argv']
    
    group_id = session.ctx['group_id']
    dm = DataManager(group_id)

    members = await session.bot.get_group_member_list(group_id=group_id)

    lines = []
    for member in members:
        alias = member['card'] if member['card'] else member['nickname']
        qq_id = member['user_id']

        accounts = dm.query_binded_accounts(qq_id)
        msg = f"{alias}: "
        if accounts:
            msg += ", ".join([f"{u}@{p}" for u, p in accounts])
        else:
            msg += "NaN"

        lines.append(msg)
    
    for msg in multiline_msg_generator(lines=lines, lineno=True):
        await session.bot.send_msg_rate_limited(group_id=group_id, message=msg)


@on_command('progress', only_to_me=False, permission=GROUP)
async def show_progress(session: CommandSession):
    """progress: 查询本周刷题进度（周日18点为界线）

用法:
progress
"""
    group_id = session.ctx['group_id']
    qq_id = session.ctx['user_id']

    dm = DataManager(group_id)

    accounts = dm.query_binded_accounts(qq_id)

    starttime = last_sunday()
    endtime = dm.get_latest_csttime_by_qq(qq_id)

    vs, ve = dm.report_by_qq(qq_id, starttime, endtime)

    tf = "%Y/%m/%d %H:%M"

    msg = f"""Progress this week:
[{starttime.strftime(tf)}] Accepted: {vs}
[{endtime.strftime(tf)}] Accepted: {ve} (+{ve-vs})"""
    
    await session.send(msg)


@on_command('update', only_to_me=False, permission=GROUP)
async def update_database(session: CommandSession):
    """update: 立刻更新账号数据（冷却时间10分钟）
除此之外，爬虫会在每日18点左右自动更新账号数据（如有bug请 @Nuullll）

用法:
update
"""
    group_id = session.ctx['group_id']
    qq_id = session.ctx['user_id']
    debug = session.ctx.get('debug', False)

    if not debug:
        dm = DataManager(group_id)
        accounts = dm.query_binded_accounts(qq_id)

        await session.send("正在更新数据", at_sender=True)

        if not accounts:
            await session.finish("请先绑定账号！命令：register")

        latest = dm.get_latest_csttime_by_qq(qq_id)
        now = cstnow()
        delta = int((now - latest).total_seconds())
        print(latest, now, delta)

        await session.send(f"最近更新: {latest}")
        if delta < USER_UPDATE_COOLDOWN:
            await session.finish(f"技能冷却中：剩余{USER_UPDATE_COOLDOWN-delta}秒")
        
        for user_id, platform in accounts:
            ok, snapshot = await dm.get_and_save_user_summary(qq_id, user_id, platform)
        
            if not ok:
                await session.send("ID错误或网络错误！请检查后重试。")
                
            for msg in multiline_msg_generator(snapshot.lines):
                await session.bot.send_msg_rate_limited(group_id=group_id, message=msg)
    else:
        dm = DataManager(group_id)
        accounts = dm.query_binded_accounts(qq_id)
        
        for user_id, platform in accounts:
            ok, snapshot = await dm.get_and_save_user_summary(qq_id, user_id, platform)
                
            for msg in multiline_msg_generator(snapshot.lines):
                await session.bot.send_msg_rate_limited(user_id=724463877, message=msg)


@on_command('report', permission=GROUP_ADMIN)
async def report(session: CommandSession):
    group_id = session.ctx['group_id']

    dm = DataManager(group_id)

    starttime = last_sunday()
    endtime = cstnow()

    data = dm.report(starttime, endtime)
    data = [[alias, ac_now, ac_now - ac_before] for alias, ac_before, ac_now in data if ac_now > 0]

    data.sort(reverse=True, key=itemgetter(2, 1))

    lines = autoalign(data, formatter=lambda x: "| {} | {:<5} (+{}) |".format(*x))

    header = f"{starttime} - {endtime}\n"
    header += "｜ Name ｜ Accepted (+delta) ｜"
    await session.send(header)

    for msg in multiline_msg_generator(lines, lineno=True):
        await session.bot.send_msg_rate_limited(group_id=group_id, message=msg)


@on_command('report_total', permission=GROUP_ADMIN)
async def report_total(session: CommandSession):
    group_id = session.ctx['group_id']
    group_info = await session.bot.get_group_info(group_id=group_id)
    group_name = group_info['group_name']
    member_count = group_info['member_count']

    dm = DataManager(group_id)

    starttime = long_long_ago()
    endtime = cstnow()

    data = dm.report(starttime, endtime)
    data = [[alias, ac_now] for alias, _, ac_now in data if ac_now > 0]

    data.sort(reverse=True, key=itemgetter(1))

    lines = autoalign(data, formatter=lambda x: "| {} | {:<5} |".format(*x))

    entries = min(member_count, REPORT_TOTAL_MAX_ENTRIES, len(data))
    header = f"{group_name} Top {entries} / {member_count}\n"
    header += "# ｜ Name ｜ Accepted ｜"
    await session.send(header)

    for msg in multiline_msg_generator(lines[:entries], lineno=True):
        await session.bot.send_msg_rate_limited(group_id=group_id, message=msg)


@on_command('update_all', permission=GROUP_ADMIN)
async def update_all(session: CommandSession):
    group_id = session.ctx['group_id']

    dm = DataManager(group_id)

    members = await session.bot.get_group_member_list(group_id=group_id)
    await session.send("开始强制更新...")

    for member in members:
        print(member)
        ctx = {'debug': True, 'anonymous': None, 'font': 1623440, 'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': 'report'}}], 'message_id': 20804, 'message_type': 'group', 'post_type': 'message', 'raw_message': 'report', 'self_id': 2210705648, 'sender': {'age': 24, 'area': '北京', 'card': '', 'level': '冒泡', 'nickname': 'Nuullll', 'role': 'owner', 'sex': 'unknown', 'title': '', 'user_id': 724463877}, 'sub_type': 'normal', 'time': 1584248424, 'user_id': 724463877, 'to_me': True}
        ctx['sender'].update(member)
        ctx['user_id'] = member['user_id']
        await call_command(nonebot.get_bot(), ctx, 'update')
    
    await session.finish("手动更新成功！")