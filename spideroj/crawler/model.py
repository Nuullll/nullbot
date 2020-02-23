import importlib


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
    def lines(self):
        lines = []
        for field in self.fields:
            lines.append(field.serialize(self.data.get(field.name, 'NaN'))
        
        return lines

    @property
    def accepted(self):
        name = 'Solved Question'

        ac = self.data.get(name, 'NaN')
        if isinstance(ac, list):
            ac = ac[0]
        
        return ac