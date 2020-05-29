from nonebot import on_natural_language, NLPSession
from nonebot.permission import GROUP, GROUP_ADMIN, SUPERUSER
from nullbot.config import MONITOR_RECENT_MESSAGES, REPEAT_THRESHOLD, TURINGBOT_API_URL, TURINGBOT_API_KEY
from collections import defaultdict
from nullbot.utils.helpers import get_random_header
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import random


RECENT = defaultdict(list)
FREQ = defaultdict(lambda: defaultdict(lambda:0))
LAST_SENT = defaultdict(str)

TURINGBOT_API_INVOKED = 0


@on_natural_language(only_to_me=False, permission=GROUP)
async def repeat_bullshit(session: NLPSession):
    group_id = session.ctx['group_id']

    msg = session.msg.strip()
    if msg == LAST_SENT[group_id]:
        return

    RECENT[group_id].append(msg)
    FREQ[group_id][msg] += 1

    if len(RECENT[group_id]) > MONITOR_RECENT_MESSAGES:
        trash = RECENT[group_id].pop(0)
        FREQ[group_id][trash] -= 1
        if FREQ[group_id][trash] == 0:
            del FREQ[group_id][trash]
    
    if FREQ[group_id][msg] >= REPEAT_THRESHOLD:
        await session.send(msg)
        LAST_SENT[group_id] = msg

        print(f"Bullshit repeated: {msg}")
        print(f"RECENT: {RECENT}")


@on_natural_language(permission=GROUP)
async def reply_cue_me(session: NLPSession):

    if TURINGBOT_API_INVOKED >= 450:
        await session.finish(get_random_header() + "\n今天聊够了，下班。")

    text = session.msg_text

    reply = await request_turing_api(text)

    if reply:
        await session.send(reply)


@on_natural_language(only_to_me=False, permission=GROUP)
async def random_bullshit(session: NLPSession):

    if TURINGBOT_API_INVOKED >= 450:
        return

    now = datetime.now()
    zero = now.replace(hour=0, minute=0, second=0)
    tomorrow = zero + timedelta(days=1)
    seconds_to_waste = (tomorrow - now).total_seconds()

    p = (500 - TURINGBOT_API_INVOKED) / seconds_to_waste
    print(p)
    if random.random() < p:
        # call api

        text = session.msg_text
        reply = await request_turing_api(text)

        if reply:
            await session.send(reply)


async def request_turing_api(message, user_id=0, group_id=0, user_nickname=''):

    payload = {
        'reqType': 0,
        'perception': {
            'inputText': {
                'text': message
            }
        },
        'userInfo': {
            'apiKey': TURINGBOT_API_KEY,
            'userId': user_id,
            'groupId': group_id,
            'userIdName': user_nickname
        }
    }

    reply = ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(TURINGBOT_API_URL, json=payload) as res:
                if res.status == 200:
                    data = json.loads(await res.text())
                    print(data)

                    for result in data['results']:
                        reply += "\n".join(result["values"].values())
    except:
        return ""

    return reply