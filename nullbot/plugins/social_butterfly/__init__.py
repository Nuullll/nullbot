import nonebot
from nonebot import on_request
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GroupRequestEvent

matcher = on_request()

@matcher.handle()
async def _(bot: Bot, event: GroupRequestEvent):
  if event.sub_type == "invite":
    await bot.send_group_msg(group_id=event.group_id, message="大家好，我是闹闹～")
