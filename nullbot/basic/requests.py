from nonebot import on_request, RequestSession


@on_request('group')
async def handle_group_invitation(session: RequestSession):
    if session.ctx['sub_type'] == 'invite':
        if session.ctx['user_id'] in session.bot.config.SUPERUSERS:
            await session.approve()
