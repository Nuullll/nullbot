from nonebot import on_command, on_request, on_notice, CommandSession, RequestSession, NoticeSession


@on_command('test_send_private_msg', aliases=('私聊测试', ))
async def test_send_private_msg(session: CommandSession):
    info = await session.bot.send_private_msg(user_id=724463877, message='测试成功')


@on_request('group')
async def test_handle_group_invitation(session: RequestSession):
    if session.ctx['sub_type'] == 'invite':
        if session.ctx['user_id'] in session.bot.config.SUPERUSERS:
            await session.approve()


@on_command('test_at')
async def test_at(session: CommandSession):
    await session.send('欢迎[CQ:at,qq=724463877]')
