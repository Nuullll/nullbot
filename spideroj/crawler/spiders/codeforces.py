from spideroj.crawler.spiders import Spider
from spideroj.crawler.field import Field
from spideroj.crawler.processor import Cleaner
from datetime import datetime, timezone


class CodeforcesSpider(Spider):
    server_name = 'codeforces'
    spider_type = 'submission'
    submission_url = 'http://codeforces.com/submissions/{}/page/{}'

    fields = [
        Field(
            name='Solved Question',
            xpath_selector='generated dynamically',
        ),

        Field(
            name='Rank Title',
            xpath_selector='//*[@id="pageContent"]/div[2]/div[5]/div[2]/div/div[1]/span/text()',
        ),

        Field(
            name='Contest Rating',
            xpath_selector='//*[@id="pageContent"]/div[2]/div[5]/div[2]/ul/li[1]/span[1]/text()',
        ),

        Field(
            name='Highest Title',
            xpath_selector='//*[@id="pageContent"]/div[2]/div[5]/div[2]/ul/li[1]/span[2]/span[1]/text()',
            cleaner=lambda x: x.strip(', ')
        ),

        Field(
            name='Highest Rating',
            xpath_selector='//*[@id="pageContent"]/div[2]/div[5]/div[2]/ul/li[1]/span[2]/span[2]/text()',
        ),

        Field(
            name='Contributions',
            xpath_selector='//*[@id="pageContent"]/div[2]/div[5]/div[2]/ul/li[2]/span/text()',
        ),
    ]

    async def get_new_submissions(self, username, last_submission_id=-1):
        has_next = True
        page = 1

        new_submissions = []
        ac_set = set()

        try:
            while has_next:
                has_next, submissions = await self.parse_submission_page(username, page)
                page += 1

                for sub in submissions:
                    if last_submission_id == sub['id']:
                        has_next = False
                        break

                    problem_id = sub['problem']['id']
                    if problem_id not in ac_set:
                        ac_set.add(problem_id)
                        new_submissions.append(sub)
        except Exception as e:
            print(e)
            return False, {}
        
        data = {
            'submissions': new_submissions,
            'accepted_problem_ids': ac_set,
        }

        return True, data
            


    async def parse_submission_page(self, username, page=1):
        url = self.submission_url.format(username, page)

        ok, context = await self.get_page(url, self.js_support)

        if not ok:
            print("Failed to get submission page {} of [{}]".format(page, username))
            return False, []

        rows = context.find('table.status-frame-datatable tr:not(.first-row)')

        accepted_submissions = []
        for row in rows:
            submission_id = int(row.attrs.get("data-submission-id", "-1"))
            cells = row.find("td")

            verdict = cells[-3]
            status = verdict.find("span.submissionVerdictWrapper", first=True).attrs.get("submissionverdict", "fail").upper()
            
            if status != "OK":
                continue
            
            timestamp = cells[1]
            dt = datetime.strptime(timestamp.text, "%b/%d/%Y %H:%M")
            ts = dt.replace(tzinfo=timezone.utc).timestamp()

            problem = cells[3]
            problem_id = int(problem.attrs.get("data-problemid", "-1"))
            a = problem.find("a", first=True)
            
            problem_name, contest = "", ""
            if a:
                problem_name = a.text.strip()
                contest = a.attrs.get("href", "")
                
            accepted_submissions.append({
                'id': submission_id,
                'verdict': status,
                'timestamp': ts,
                'problem': {
                    'id': problem_id,
                    'name': problem_name,
                    'contest': contest
                }
            })
        
        pages = context.find('.pagination span.page-index')
        last_page = int(pages[-1].attrs.get("pageindex", 1))
        
        has_next = page < last_page
        
        return has_next, accepted_submissions