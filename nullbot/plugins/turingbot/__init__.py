import nonebot
from nonebot import on_message
from nonebot.adapters.cqhttp import Bot, MessageEvent
from .model import get_reply_strategy
from .config import Config

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

matcher = on_message(priority=2, block=False)
strategy = get_reply_strategy()

@matcher.handle()
async def turingbot_reply(bot: Bot, event: MessageEvent):
  await strategy.process(event, matcher)
