import importlib
from nullbot.utils.helpers import utc_ts_to_cst_dt


class Snapshot(object):

    def __init__(self, user_id, platform, timestamp, data, **kargs):
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
    def cst_time(self):
        return utc_ts_to_cst_dt(self.timestamp)
    
    @property
    def lines(self):
        result = [
            f"{self.user_id}@{self.platform}",
            "Timestamp: " + self.cst_time.strftime("%Y-%m-%d %H:%M:%S CST")
        ]
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