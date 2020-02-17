from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner


class HduSpider(Spider):
    server_name = 'hdu'

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='/html/body/table/tr[4]/td/table/tr/td/table/tr[4]/td[2]/text()'
        ),

        Field(
            name='Global Ranking',
            xpath_selector='/html/body/table/tr[4]/td/table/tr/td/table/tr[2]/td[2]/text()',
        ),
    ]
