import httpx
import json
from datetime import datetime
import random
import nonebot
from nonebot.adapters.cqhttp import MessageEvent
from nonebot.matcher import Matcher
from nonebot.log import logger
from .config import Config

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

def refresh_quota_daily(last_timestamp: datetime):
  if last_timestamp is None:
    return True
  now = datetime.now()
  return now.date() != last_timestamp.date()

class ReplyStrategy:
  def __init__(self, predicate_func, refresh_quota_func = refresh_quota_daily, quota_limit = float('inf')):
    self.predicate = predicate_func
    self.refresh = refresh_quota_func
    self.quota_limit = quota_limit
    self.quota_used = 0
    self.last_message_timestamp = None
  
  def is_available(self):
    if self.refresh(self.last_message_timestamp):
      self.quota_used = 0
    
    return self.quota_used < self.quota_limit
  
  async def process(self, event: MessageEvent, matcher: Matcher):
    self.last_message_timestamp = datetime.now()
    if not self.is_available():
      return

    if self.predicate(event):
      reply = await self.request_api(event)
      logger.debug(f"Turingbot reply: {reply}")
      if reply:
        await matcher.send(reply)

  async def request_api(self, event: MessageEvent):
    message = str(event.get_message())
    user_id = event.get_user_id()
    user_nickname = event.sender.nickname
    payload = {
      'reqType': 0,
      'perception': {
        'inputText': {
          'text': message
        }
      },
      'userInfo': {
        'apiKey': plugin_config.turingbot_api_key,
        'userId': user_id,
        'userIdName': user_nickname
      }
    }

    try:
      async with httpx.AsyncClient() as client:
        r = await client.post(plugin_config.turingbot_api_url, json=payload)
        if r.status_code == 200:
          self.quota_used += 1
          data = json.loads(r.text)
          logger.debug(f"Got turingapi data: {data}")
          if data['intent']['code'] == 4003:
            self.quota_used = self.quota_limit
            logger.warning("Reached turingapi limit!")
            return ""
          
          reply = ""
          for result in data['results']:
            reply += "\n".join(result['values'].values())
          
          return reply
    except Exception as e:
      logger.warning(f"Exception calling turingapi: {e}")
    return ""

class UniformProbStrategy(ReplyStrategy):
  @staticmethod
  def predicate(_: MessageEvent):
    t = random.uniform(0, 1)
    logger.debug(f"Uniform strategy predicate: {t}")
    return t < plugin_config.uniform_prob

  def __init__(self):
    super().__init__(UniformProbStrategy.predicate, refresh_quota_daily, plugin_config.daily_api_quota)

def get_reply_strategy():
  if plugin_config.strategy == "uniform":
    return UniformProbStrategy()
  raise NotImplementedError(f"{plugin_config.strategy} reply strategy not implemented!")
