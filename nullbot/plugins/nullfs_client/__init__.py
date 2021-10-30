import httpx
import nonebot
from nonebot import on_message
from nonebot.log import logger
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from .config import Config

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

def mount_nullfs():
  with httpx.Client() as client:
    client.post(f"{plugin_config.nullfs_api_url}/mount", data={'mount_point': plugin_config.nullfs_mount_point})

matcher = on_message(priority=1, block=False, permission=SUPERUSER)

@matcher.handle()
async def nullfs_entry(bot: Bot, event: MessageEvent, matcher: Matcher):
  message = str(event.get_message()).strip()
  cmd_args = message.split()
  if len(cmd_args) == 0:
    return

  cmd = cmd_args[0]
  async with httpx.AsyncClient() as client:
    mount_nullfs()
    nullfs_api = plugin_config.nullfs_api_url
    r = await client.get(f"{nullfs_api}/supports?cmd={cmd}")
    if r.status_code == 200:
      user_id = event.user_id
      cmd_res = await client.put(f"{nullfs_api}/user/{user_id}/{cmd}", data={'arg': cmd_args[1:]})
      if cmd_res.status_code == 200:
        data = cmd_res.json()['data']
        logger.debug(data)
        await matcher.send(str(data))
        matcher.stop_propagation()
