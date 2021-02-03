import nonebot as nb
from nullbot.config import AUTO_UPDATES, AUTO_DAILY_REPORT, AUTO_UPDATE_MAX_RETRIES, AUTO_BLOG_PUSHES
from spideroj.mongo import DataManager
from datetime import datetime
from nonebot.command import call_command
from nullbot.utils.helpers import get_fake_cqevent, guess_blog_update_time, multiline_msg_generator, render_cq_at
import pytz


async def debug(msg):
    bot = nb.get_bot()

    await bot.send_private_msg(user_id=724463877, message=msg)


# @nb.scheduler.scheduled_job('cron', minute='*')
# async def heartbeat():
#     bot = nb.get_bot()
#     print(await bot.get_status())


@nb.scheduler.scheduled_job('cron', hour='18')
async def daily_update():
    bot = nb.get_bot()

    checkpoint = set()
    for group_id in AUTO_UPDATES:
        await debug(f"Updating for group: {group_id}")
        dm = DataManager(group_id)

        members = await bot.get_group_member_list(group_id=group_id)
        dm.init(members)

        fails, successes = await dm.get_and_save_all_user_summary(checkpoint)

        await debug(f"Group [{group_id}] update failures: {fails}")

        retry = 0
        _fails = fails[:]
        while fails:
            fails = []
            for qq_id, user_id, platform in _fails:
                ok, snapshot = await dm.get_and_save_user_summary(qq_id, user_id, platform)

                if not ok:
                    fails.append((qq_id, user_id, platform))
                else:
                    successes.append((qq_id, user_id, platform))
            
            retry += 1
            if retry >= AUTO_UPDATE_MAX_RETRIES:
                await debug(f"Failures after {AUTO_UPDATE_MAX_RETRIES} retries: {fails}")
                break

            _fails = fails[:]

        checkpoint.update(successes)
    
    for group_id, mode in AUTO_DAILY_REPORT.items():
        event = get_fake_cqevent(group_id=group_id)
        if mode == 'week_delta':
            await call_command(bot, event, 'report')
        else:
            await call_command(bot, event, 'report_total')


# @nb.scheduler.scheduled_job('cron', hour='8')
# async def get_latest_blogs():
#     # query all
#     recent_updated = []
#     now = datetime.now()

#     url_map = DataManager.query_blog()
#     for qq_id, blog_urls in url_map.items():
#         for url in blog_urls:
#             text, dt = guess_blog_update_time(url)

#             if text is None:
#                 continue

#             if (now - dt).days <= 2:
#                 recent_updated.append((qq_id, url, dt.strftime("%Y-%m-%d")))
    
#     if not recent_updated:
#         return

#     lines = [f"{render_cq_at('all')} 以下博客近2天内有更新，大家快去学习吧"]
#     for qq_id, url, dt_str in recent_updated:
#         line = f"{render_cq_at(qq_id)} {url} {dt_str}"
#         lines.append(line)
    
#     for group_id in AUTO_BLOG_PUSHES:
#         for msg in multiline_msg_generator(lines=lines, lineno=False):
#             await nb.get_bot().send_msg(group_id=group_id, message=msg)