MEMBER_DB = 'oj'
OJID_DB = 'ids'
SNAPSHOT_DB = 'snapshots'

PLATFORM_URLS = {
    'leetcode': r'https://leetcode.com/{}',
    'leetcodecn': r'https://leetcode-cn.com/u/{}',
    'luogu': r'https://www.luogu.com.cn/user/{}',
    'lintcode': r'https://www.lintcode.com/user/{}',
    'hdu': r'http://acm.hdu.edu.cn/userstatus.php?user={}',
    'vjudge': r'https://vjudge.net/user/{}',
}

CRAWL_URLS = {
    'lintcode': r'https://www.lintcode.com/api/accounts/{}/profile/?format=json'
}

# splash js rendering service
SPLASH_API_ROOT = 'http://172.18.0.1:8050/render.html'
SPLASH_QUERY = '?url={}&engine=chromium&wait=6&timeout=60&rend_all=1'
