from nullbot.config import MAX_MESSAGE_LEN
from nonebot import CommandSession
import re


def multiline_msg_generator(lines=None, lineno=False, lineno_format='#{} ', max_msg_len=MAX_MESSAGE_LEN):
    msg = ''
    sz = 0
    for i, line in enumerate(lines):
        if lineno:
            msg += lineno_format.format(i)

        msg += line + '\n'
        sz += len(line)

        if sz > max_msg_len:
            yield msg.strip()
            msg = ''
            sz = 0
    
    yield msg.strip()


def validate_role(session: CommandSession, expected=('owner', 'admin')):
    try:
        role = session.ctx['sender'].get('role', 'member')
    except Exception:
        return False

    return role in expected


is_admin = lambda s: validate_role(s, ('owner', 'admin'))
is_owner = lambda s: validate_role(s, ('owner', ))


def parse_cq_at(cqcode):
    m = re.search(r'\[CQ:at,qq=(\d+)\]', cqcode)
    if m:
        return int(m.group(1))
    
    raise ValueError("Parse CQ error.")