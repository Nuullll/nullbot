from nullbot.config import MAX_MESSAGE_LEN
from nonebot import CommandSession
import re
from datetime import datetime, timezone, timedelta
import pytz

CST = pytz.timezone("Asia/Shanghai")


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


def utc_ts_to_dt(utc_ts):
    return datetime.fromtimestamp(utc_ts, timezone.utc)


def utc_dt_to_ts(utc_dt):
    return datetime.timestamp(utc_dt)


def utc_ts_to_cst_dt(utc_ts):
    utc_dt = utc_ts_to_dt(utc_ts)
    cst_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(CST)

    return CST.normalize(cst_dt)


def cst_dt_to_utc_ts(cst_dt):
    utc_dt = cst_dt.replace(tzinfo=CST).astimezone(pytz.utc)
    utc_dt = pytz.utc.normalize(utc_dt)

    return utc_dt_to_ts(utc_dt)


def last_sunday(hour=18, minute=0):
    today = datetime.today()
    wd = today.weekday()

    last = today - timedelta(days=wd+1)
    return last.replace(hour=hour, minute=minute)


def print_width(s):
    """
    Calculate the print width of string `s` on the console.
    """
    x = len(s)
    y = len(re.sub(r'[^\u0001-\u007f]+', r'', s))

    return 2 * x - y


def autoalign(lines, formatter=lambda line: repr(line), align_key=0):
    max_width = 0

    for line in lines:
        max_width = max(max_width, print_width(line[align_key]))
    
    result = []

    for line in lines:
        width = print_width(line[align_key])
        line[align_key] += ' ' * (max_width - width)

        result.append(formatter(line))
    
    return result
