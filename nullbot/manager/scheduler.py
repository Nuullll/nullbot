import nonebot as nb
from nullbot.config import AUTO_UPDATES, AUTO_DAILY_REPORT, AUTO_UPDATE_MAX_RETRIES
from spideroj.mongo import DataManager
from datetime import datetime
from nonebot.command import call_command
from nullbot.utils.helpers import get_fake_cqevent
import pytz


async def debug(msg):
    bot = nb.get_bot()

    await bot.send_private_msg(user_id=724463877, message=msg)


@nb.scheduler.scheduled_job('cron', hour='18')
async def daily_update():
    bot = nb.get_bot()

    for group_id in AUTO_UPDATES:
        await debug(f"Updating for group: {group_id}")
        dm = DataManager(group_id)

        members = await bot.get_group_member_list(group_id=group_id)
        dm.init(members)

        fails = await dm.get_and_save_all_user_summary()

        await debug(f"Group [{group_id}] update failures: {fails}")

        retry = 0
        while fails:
            fails = []
            for qq_id, user_id, platform in fails:
                ok, snapshot = await dm.get_and_save_user_summary(qq_id, user_id, platform)

                if not ok:
                    fails.append((qq_id, user_id, platform))
            
            retry += 1
            if retry >= AUTO_UPDATE_MAX_RETRIES:
                await debug(f"Failures after {AUTO_UPDATE_MAX_RETRIES} retries: {fails}")
                break
    
    for group_id, mode in AUTO_DAILY_REPORT.items():
        event = get_fake_cqevent(group_id=group_id)
        if mode == 'week_delta':
            await call_command(bot, event, 'report')
        else:
            await call_command(bot, event, 'report_total')
