import nonebot as nb
from spideroj.crawler.spiders import Spider
from datetime import datetime
import pytz


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