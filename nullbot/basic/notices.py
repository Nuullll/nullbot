from nonebot import on_notice, NoticeSession


@on_notice('group_increase')
async def test_handle_group_increase(session: NoticeSession):
    user_id = session.ctx['user_id']
    await session.send(f'''欢迎大佬! [CQ:at,qq={user_id}]
发送help，可查看闹闹支持的命令''')
