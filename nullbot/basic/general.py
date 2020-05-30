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


# @on_natural_language(permission=GROUP)
# async def reply_cue_me(session: NLPSession):
#     global TURINGBOT_API_INVOKED
#     print(TURINGBOT_API_INVOKED)

#     if TURINGBOT_API_INVOKED >= 500:
#         await session.send(get_random_header() + "\n今天聊够了，下班。")
#         return 

#     text = session.msg_text
#     qq_id = session.event.user_id
#     group_id = session.event.group_id
#     card = session.event.sender.get('card', 'nobody')

#     TURINGBOT_API_INVOKED += 1
#     reply = await request_turing_api(text, user_id=qq_id, group_id=group_id, user_nickname=card)

#     if reply:
#         await session.send(reply)


@on_natural_language(only_to_me=False, permission=GROUP)
async def random_bullshit(session: NLPSession):

    now = datetime.now()
    flag = random.randint(0, 59)
    print(now.second, flag)
    if now.second == flag:
        # call api

        text = session.msg_text
        reply = await request_turing_api(text, user_id=qq_id, group_id=group_id, user_nickname=card)

        if reply:
            await session.send(reply)


async def request_turing_api(message, user_id=0, group_id=0, user_nickname=''):
    global TURINGBOT_API_INVOKED

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

                    if data['intent']['code'] == 4003:
                        TURINGBOT_API_INVOKED = 500
                        return ""

                    for result in data['results']:
                        reply += "\n".join(result["values"].values())
    except Exception as e:
        print(e)
        return ""

    return reply