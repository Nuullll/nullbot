from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner


class LuoguSpider(Spider):
    server_name = 'luogu'
    js_support = True

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[4]/a/span[2]/text()',
        ),

        Field(
            name='Submission',
            xpath_selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[3]/a/span[2]/text()'
        ),

        Field(
            name='Ranking',
            xpath_selector='//*[@id="app"]/div[2]/main/div/div[1]/div[2]/div[2]/div/div[5]/div/span[2]/text()'
        )
    ]
