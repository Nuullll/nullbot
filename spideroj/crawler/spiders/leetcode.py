from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner


class LeetcodeSpider(Spider):
    server_name = 'leetcode'
    use_oversea_remote_server = True
    js_support = True

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='/html/body/div[1]/div[2]/div/div[2]/div[1]/div[last()]/div/div/div[1]/div[1]/div[2]/text()'
        ),

        Field(
            name='Finished Contests',
            xpath_selector='/html/body/div[1]/div[2]/div/div[2]/div[1]/div[last()-1]/div/div/div[3]/div[2]/div/div[2]/text()',
        ),

        Field(
            name='Rating',
            xpath_selector='/html/body/div[1]/div[2]/div/div[2]/div[1]/div[last()-1]/div/div/div[1]/div[1]/div/div/div[2]/text()',
        ),

        Field(
            name='Global Ranking',
            xpath_selector='/html/body/div[1]/div[2]/div/div[2]/div[1]/div[last()-1]/div/div/div[3]/div[1]/div/div[2]/text()',
        ),

        # Field(
        #     name='Accepted Submission',
        #     xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[2]/span/text()',
        #     cleaner=Cleaner.get_fraction
        # ),

        # Field(
        #     name='Acceptance Rate',
        #     xpath_selector='string(/html/body/div[1]/div[2]/div/div[2]/div[1]/div[last()]/div/div/div[1]/div[2]/div[2]/div/div[1])',
        #     cleaner=Cleaner.get_percent
        # )
    ]
