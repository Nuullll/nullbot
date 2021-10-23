import nonebot
from nonebot import on_message
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from .config import Config
from .model import LFUCache, LFUNode

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

matcher = on_message(priority=10, block=False)

async def callback(node: LFUNode):
  if node.count == plugin_config.repeat_threhold:
    logger.info(f"Repeating bullshit: {node.key}")
    await node.object.send(node.key)

message_cache = LFUCache(plugin_config.cache_capacity, callback)

@matcher.handle()
async def _(bot: Bot, event: Event):
  await message_cache.put(str(event.get_message()).strip(), matcher)
