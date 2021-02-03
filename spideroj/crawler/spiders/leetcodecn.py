import re
from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner


class LeetcodecnSpider(Spider):
    server_name = 'leetcodecn'
    js_support = True

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[last()-1]/div[1]/div/b/text()'
        ),

        Field(
            name='Finished Contests',
            xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[last()-2]/div[3]/div[3]/b/text()',
        ),

        Field(
            name='AC Ranking',
            xpath_selector='/html/body/div[1]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/span[2]/text()'
        ),

        # Field(
        #     name='Accepted Submission',
        #     xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div[4]/div[3]/span/text()',
        #     cleaner=Cleaner.get_fraction
        # ),

        # Field(
        #     name='Acceptance Rate',
        #     xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[5]/div[last()-1]/div[2]/div/div[1]/text()',
        #     cleaner=Cleaner.get_percent
        # ),

        Field(
            name='National Ranking',
            xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[last()-2]/div[3]/div[1]/b/text()'
        ),

        Field(
            name='Global Ranking',
            xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[last()-2]/div[3]/div[2]/b/text()'
        ),

        Field(
            name='Contest Rating',
            xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[last()-2]/div[1]/header/div[1]/b/text()',
        ),

        Field(
            name='Badges',
            xpath_selector='/html/body/div[1]/div/div[2]/div/div[2]/div[1]/div/div[1]/div[last()]/div[1]/div[1]/div/b/text()'
        )
    ]
