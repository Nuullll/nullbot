from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner


class LeetcodeSpider(Spider):
    server_name = 'leetcode'

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[1]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Finished Contests',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[1]/span/text()',
        ),

        Field(
            name='Rating',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[2]/span/text()',
        ),

        Field(
            name='Global Ranking',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[2]/ul/li[3]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Accepted Submission',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[2]/span/text()',
            cleaner=Cleaner.get_fraction
        ),

        Field(
            name='Acceptance Rate',
            xpath_selector='//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[3]/span/text()',
            cleaner=Cleaner.get_percent
        )
    ]
