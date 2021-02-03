from requests_html import AsyncHTMLSession
import json
import importlib
from spideroj.config import PLATFORM_URLS, CRAWL_URLS, SPLASH_API_ROOT, SPLASH_QUERY, REMOTE_SPLASH_API_ROOT
from urllib.parse import urlencode


class Spider(object):
    
    server_name = ''
    fields = []
    use_oversea_remote_server = False
    js_support = False
    spider_type = 'summary'     # or 'submission'

    @staticmethod
    async def get_page(url, js_support=False, use_oversea_remote_server=False):
        if use_oversea_remote_server:
            return await Spider.render_html_with_remote_splash(url)

        if js_support:
            return await Spider.render_html_with_splash(url)
        
        session = AsyncHTMLSession()

        r = await session.get(url)

        if r.status_code == 200:
            return True, r.html

        return False, None

    @classmethod
    def parse_fields(cls, context):
        data = {}

        for field in cls.fields:
            if field.xpath_selector:
                try:
                    print(context)
                    raw = context.xpath(field.xpath_selector)
                    cleaned = field.cleaner(raw[0])
                    data[field.name] = cleaned
                except Exception as e:
                    print("WARNING: Failed to retrieve Field [{}] ({})".format(field.name, e))
            else:
                obj = json.loads(context.text)

                try:
                    cleaned = field.json_parser(obj)
                    data[field.name] = cleaned
                except Exception as e:
                    print("WARNING: Failed to retrieve Field [{}] ({})".format(field.name, e))

        return data

    @staticmethod
    def get_spider(platform):
        classname = platform.capitalize() + 'Spider'

        m = importlib.import_module('.' + platform, 'spideroj.crawler.spiders')
        c = getattr(m, classname)

        if platform in CRAWL_URLS:
            server_url = CRAWL_URLS[platform]
        else:
            server_url = PLATFORM_URLS[platform]
        
        return c(server_url)
    
    @classmethod
    async def render_html_with_splash(cls, url):
        try:
            session = AsyncHTMLSession()
            splash_url = SPLASH_API_ROOT + SPLASH_QUERY.format(url)

            # if cls.server_name == 'leetcodecn':
            #     splash_url += '&' + urlencode({'lua_source': SPLASH_LUA_SOURCE_LEETCODECN})

            r = await session.get(splash_url)

            if r.status_code == 200:
                return True, r.html
        except:
            pass

        return False, None

    @classmethod
    async def render_html_with_remote_splash(cls, url):
        try:
            session = AsyncHTMLSession()
            remote_splash_url = REMOTE_SPLASH_API_ROOT + SPLASH_QUERY.format(url)
            print(remote_splash_url)

            r = await session.get(remote_splash_url)

            if r.status_code == 200:
                return True, r.html
        except:
            pass

        return False, None

    def __init__(self, server_url):
        self.server_url = server_url

    def get_user_url(self, username):
        return self.server_url.format(username)
        
    async def get_user_data(self, username):
        url = self.get_user_url(username)

        ok, context = await self.get_page(url, self.js_support, self.use_oversea_remote_server)

        if not ok:
            print("Failed to get profile page of [{}]".format(username))
            return False, {}

        data = self.parse_fields(context)
        # print("[{}@{}]: {}".format(username, self.server_name, data))
        if not data:
            print("ID error or Network error. No data was retrieved. [{}]".format(username))
            return False, {}

        return True, data

    async def get_new_submissions(self, username, last_submission_id=-1):
        raise NotImplementedError(f"get_new_submissions not implemented for {self.__class__}")