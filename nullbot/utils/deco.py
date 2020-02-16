from nonebot import CommandSession
from nullbot.config import SUPERUSERS
from nullbot.utils.helpers import is_admin, is_owner


# restrict command scope
def command_scope_deco(validate_func, message=''):
    def deco(command_handler):
        async def wrapper(session: CommandSession):
            if validate_func(session):
                return await command_handler(session)
            
            if message:
                await session.send(message)
            
            return
        
        return wrapper
    
    return deco


group_only = command_scope_deco(lambda s: 'group_id' in s.ctx, message='Group-only command.')
superuser_only = command_scope_deco(lambda s: s.ctx['user_id'] in SUPERUSERS, message='Permission denied. [SUPERUSER]')
admin_only = command_scope_deco(is_admin, message='Permission denied. [ADMIN]')
owner_only = command_scope_deco(is_owner, message='Permission denied. [OWNER]')