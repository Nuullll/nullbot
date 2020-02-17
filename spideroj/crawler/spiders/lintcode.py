from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner


class LintcodeSpider(Spider):
    server_name = 'lintcode'

    fields = [
        Field(
            name='Solved Question',
            json_parser=lambda x: [x['user_summary']['problem']['total_accepted'],
                                   x['user_summary']['problem']['total']]
        ),

        Field(
            name='AI Problem Submitted',
            json_parser=lambda x: [x['user_summary']['ai']['total_submitted'],
                                   x['user_summary']['ai']['total']]
        )
    ]
