import nonebot
from nonebot.adapters import Bot
from nonebot.log import logger

driver = nonebot.get_driver()

@driver.on_bot_connect
async def notify_superusers(bot: Bot):
  for su in driver.config.superusers:
    logger.info(f"Notifying superuser {su} on bot connect")
    await bot.send_msg(user_id=su, message="Bot connected to protocol server!")
