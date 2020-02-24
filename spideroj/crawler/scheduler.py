import asyncio
from datetime import datetime
import os
import nonebot
from nullbot.config import AUTO_UPDATES, AUTO_DAILY_REPORT
from spideroj.mongo import DataManager
from nonebot.command import call_command


class CrawlTask(object):

    _instance = None
    planned = "18:00"

    @staticmethod
    def get():
        if CrawlTask._instance is None:
            return CrawlTask()
        
        return CrawlTask._instance

    def __init__(self):
        if CrawlTask._instance is None:
            CrawlTask._instance = self
            self.started = True
            self.updating = False
            self.checkpoint = os.path.join(os.path.dirname(__file__), '.checkpoint')

            self._load_checkpoint()

            print("Crawl Task Created.")
        else:
            raise Exception("Multiple CrawlTask instances are not allowed.")
    
    @property
    def today(self):
        return datetime.now().strftime("%m-%d")

    @property
    def now(self):
        return datetime.now().strftime("%H:%M")

    @property
    def done_today(self):
        return self._load_checkpoint()
    
    def _load_checkpoint(self):
        try:
            with open(self.checkpoint, "r") as f:
                date = f.readline().strip()

                return self.today == date
        finally:
            return False
    
    def _save_checkpoint(self):
        with open(self.checkpoint, "w") as f:
            f.write(self.today)

    async def monitor(self):
        while True:
            if self.now == self.planned and not self.updating and not self.done_today:
                self.updating = True
                self.debug("Scheduler: updating database.")

                for group_id in AUTO_UPDATES:
                    dm = DataManager(group_id)
                    fails = await dm.get_and_save_all_user_summary()

                    await self.debug("Update Failures: " + repr(fails))

                    if group_id in AUTO_DAILY_REPORT:
                        await call_command(nonebot.get_bot(), {'group_id': group_id}, 'report')
                
                self.updating = False
                self._save_checkpoint

            await asyncio.sleep(60)
    
    async def debug(self, msg):
        bot = nonebot.get_bot()

        await bot.send_private_msg(user_id=724463877, message=msg)