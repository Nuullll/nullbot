from nullbot.config import MAX_MESSAGE_LEN, RANDOM_HEADER, SUPERUSERS
from nonebot import CommandSession
from nonebot.plugin import PluginManager
import re
from datetime import datetime, timezone, timedelta
import pytz
import random
from aiocqhttp import Event as CQEvent
from requests_html import HTMLSession
import dateparser
from dateparser.search import search_dates
from dateparser_data.settings import default_parsers
_date_parsers = [parser for parser in default_parsers if parser != 'timestamp']
from operator import itemgetter


CST = pytz.timezone("Asia/Shanghai")


def is_superuser(session):
    return session.event.user_id in SUPERUSERS


def parse_cq_image(cq):
    if not cq.startswith('[CQ:image,'):
        return None

    try:
        items = cq.strip('[]').split(',')
        _, file, url = items
        return file, url
    except Exception as e:
        return None


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
    
    m = re.search(r'@(\d+)', cqcode)
    if m:
        return int(m.group(1))
    
    raise ValueError("Parse CQ error.")


def render_cq_at(qq_id):
    return f"[CQ:at,qq={qq_id}]"


def cstnow():
    return CST.normalize(datetime.now().replace(tzinfo=CST))


def utc_ts_to_dt(utc_ts):
    return datetime.fromtimestamp(utc_ts)


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


def long_long_ago():
    ago = datetime.today()
    return ago.replace(year=2000, tzinfo=CST)


def last_sunday(hour=18, minute=0):
    today = datetime.today()
    wd = today.weekday()

    last = today - timedelta(days=wd+1)
    return last.replace(hour=hour, minute=minute, tzinfo=CST)


def print_width(s):
    """
    Calculate the print width of string `s` on the console.
    """
    x = len(s)
    y = len(re.sub(r'[^\u0001-\u007f]+', r'', s))

    return 2 * x - y


def autoalign(lines, formatter=lambda line: repr(line), align_key=0):
    # max_width = 0

    # for line in lines:
    #     max_width = max(max_width, print_width(line[align_key]))
    
    result = []

    for line in lines:
        # width = print_width(line[align_key])
        # line[align_key] += ' ' * (max_width - width)

        result.append(formatter(line))
    
    return result


def get_all_commands():
    plugins = PluginManager._plugins

    commands = {}
    for plugin in plugins.values():
        for cmd in plugin.commands:
            commands[cmd.name[0]] = cmd

    return commands


def get_random_header():
    return random.choice(RANDOM_HEADER)


def get_fake_cqevent(**kwargs):
    ctx = {'anonymous': None, 'font': 1623440, 'group_id': 1048606265, 'message': [{'type': 'text', 'data': {'text': 'report'}}], 'message_id': 20804, 'message_type': 'group', 'post_type': 'message', 'raw_message': 'report', 'self_id': 2210705648, 'sender': {'age': 24, 'area': '北京', 'card': '', 'level': '冒泡', 'nickname': 'Nuullll', 'role': 'owner', 'sex': 'unknown', 'title': '', 'user_id': 724463877}, 'sub_type': 'normal', 'time': 1584248424, 'user_id': 724463877, 'to_me': True}
    ctx.update(kwargs)

    return CQEvent(**ctx)


def is_valid_url(url):
    session = HTMLSession()

    try:
        r = session.get(url, timeout=10)
        return r.status_code == 200
    except:
        return False
        

def guess_blog_update_time(blog_url):
    print(blog_url)
    session = HTMLSession()

    def _find_latest(datetime_list):
        now = datetime.now()
        delta = float('inf')
        latest = (None, None)
        for string, dt in datetime_list:
            days = (now - dt).days
            if 1 <= days < delta and len(string) >= 2:
                delta = days
                latest = (string, dt)
        
        return latest

    try:
        r = session.get(blog_url, timeout=10)
        if r.status_code == 200:
            text = r.html.find("body", first=True).text
            res = []
            for line in text.split():
                r = search_dates(line, languages=['en', 'zh'], settings={'PARSERS': _date_parsers, 'STRICT_PARSING': True})
                if not r:
                    r = dateparser.parse(line, languages=['en', 'zh'], settings={'PARSERS': _date_parsers, 'STRICT_PARSING': True})
                    if r:
                        res.append((line, r))
                        continue
                else:
                    res.extend(r)

            latest = _find_latest(res)
            print(latest)

            return latest
    except:
        pass

    return None, None