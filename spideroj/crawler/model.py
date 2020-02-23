import importlib
from datetime import datetime, timezone, timedelta


CST = timezone(offset=+timedelta(hours=8))


class Snapshot(object):

    def __init__(self, user_id, platform, timestamp, data):
        self.user_id = user_id
        self.platform = platform
        self.timestamp = timestamp
        self.data = data
        self.fields = self._get_platform_fields(self.platform)

    @staticmethod
    def _get_platform_fields(platform):
        classname = platform.capitalize() + 'Spider'

        m = importlib.import_module('.' + platform, 'spideroj.crawler.spiders')
        c = getattr(m, classname)

        return c.fields
    
    @property
    def utc_time(self):
        return datetime.utcfromtimestamp(self.timestamp)

    @property
    def cst_time(self):
        return CST.fromutc(self.utc_time)
    
    @property
    def lines(self):
        result = ["Timestamp: " + self.cst_time.strftime("%Y-%m-%d %H:%M:%S")]
        for field in self.fields:
            result.append(field.serialize(self.data.get(field.name, 'NaN')))
        
        return result

    @property
    def accepted(self):
        name = 'Solved Question'

        ac = self.data.get(name, 'NaN')
        if isinstance(ac, list):
            ac = ac[0]
        
        return ac