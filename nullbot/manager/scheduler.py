import nonebot as nb
from nullbot.config import AUTO_UPDATES, AUTO_DAILY_REPORT
from spideroj.mongo import DataManager
from datetime import datetime
from nonebot.command import call_command
import pytz


async def debug(self, msg):
    bot = nb.get_bot()

    await bot.send_private_msg(user_id=724463877, message=msg)


@nb.scheduler.scheduled_job('cron', hour='18')
async def daily_update():
    bot = nb.get_bot()

    for group_id in AUTO_UPDATES:
        dm = DataManager(group_id)

        members = await bot.get_group_member_list(group_id=group_id)
        dm.init(members)

        fails = await dm.get_and_save_all_user_summary()

        await self.debug(f"Group [{group_id}] update failures: {fails}")
    
    for group_id in AUTO_DAILY_REPORT:
        ctx = {'anonymous': None, 'font': 1623440, 'group_id': group_id, 'message': [{'type': 'text', 'data': {'text': 'report'}}], 'message_id': 20804, 'message_type': 'group', 'post_type': 'message', 'raw_message': 'report', 'self_id': 2210705648, 'sender': {'age': 24, 'area': '北京', 'card': '', 'level': '冒泡', 'nickname': 'Nuullll', 'role': 'owner', 'sex': 'unknown', 'title': '', 'user_id': 724463877}, 'sub_type': 'normal', 'time': 1584248424, 'user_id': 724463877, 'to_me': True}
        await call_command(bot, ctx, 'report')

# @nb.scheduler.scheduled_job('cron', hour='12')
# async def report_hns():
    
#     print("Waiting for coingecko...")
#     ok, html = await Spider.render_html_with_splash('https://www.coingecko.com/en/coins/handshake')

#     if not ok:
#         return
    
#     def get_content(xpath):
#         try:
#             return html.xpath(xpath + "/text()")[0]
#         except:
#             return ""
#     usd = get_content("/html/body/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/span[1]")
#     usd_d = get_content("/html/body/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/span[2]/span")
#     btc = get_content("/html/body/div[2]/div[3]/div[4]/div[1]/div[2]/div[3]")
#     btc_d = get_content("/html/body/div[2]/div[3]/div[4]/div[1]/div[2]/div[3]/span/span")
#     l_24h = get_content("/html/body/div[2]/div[3]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[6]/td/span[1]")
#     h_24h = get_content("/html/body/div[2]/div[3]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[6]/td/span[2]")
#     l_7d = get_content("/html/body/div[2]/div[3]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[7]/td/span[1]")
#     h_7d = get_content("/html/body/div[2]/div[3]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/table/tbody/tr[7]/td/span[2]")

#     message = f"""{datetime.now(pytz.timezone('Asia/Shanghai'))}
# HNS Hourly Report
# USD: {usd} {usd_d}
# BTC: {btc} {btc_d}
# 24h Low/High: {l_24h}/{h_24h}
# 7d Low/High: {l_7d}/{h_7d}
# """

#     bot = nb.get_bot()
#     await bot.send_msg(user_id=724463877, message=message)