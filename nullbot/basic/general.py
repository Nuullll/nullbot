from nonebot.natural_language import on_natural_language, NLPSession


RECORD = {}


@on_natural_language(only_to_me=False)
@group_only
async def repeat_bullshit(session: NLPSession):
    group_id = session.ctx['group_id']

    msg = session.msg.strip()

    if group_id not in RECORD:
        RECORD[group_id] = [msg, 1]
        return
    
    prev_msg, count = RECORD[group_id]
    print("Message [{}] repeated {} times.".format(prev_msg, count))

    if msg != prev_msg:
        RECORD[group_id] = [msg, 1]
        return
    
    if count == 3:
        await session.send(msg)
        print("Repeated bullshit: {}".format(msg))
    RECORD[group_id][1] += 1
