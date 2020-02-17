from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner


class VjudgeSpider(Spider):
    server_name = 'vjudge'

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='/html/body/div[1]/div[1]/div[3]/table/tr[4]/td/a/text()'
        ),
    ]
