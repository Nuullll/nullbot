from nonebot.natural_language import on_natural_language, NLPSession
from nonebot.permission import GROUP, GROUP_ADMIN, SUPERUSER
from nullbot.config import MONITOR_RECENT_MESSAGES, REPEAT_THRESHOLD
from collections import defaultdict


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