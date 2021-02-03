MEMBER_DB = 'oj'
OJID_DB = 'ids'
SNAPSHOT_DB = 'snapshots'
BLOG_DB = 'blogs'

PLATFORM_URLS = {
    'leetcode': r'https://leetcode.com/{}',
    'leetcodecn': r'https://leetcode-cn.com/u/{}',
    'luogu': r'https://www.luogu.com.cn/user/{}',
    'lintcode': r'https://www.lintcode.com/user/{}',
    'hdu': r'http://acm.hdu.edu.cn/userstatus.php?user={}',
    'vjudge': r'https://vjudge.net/user/{}',
    'codeforces': r'http://codeforces.com/profile/{}'
}

CRAWL_URLS = {
    'lintcode': r'https://www.lintcode.com/api/accounts/{}/profile/?format=json'
}

# splash js rendering service
SPLASH_API_ROOT = 'http://172.18.0.1:8050/render.html'
SPLASH_QUERY = '?url={}&engine=chromium&wait=10&timeout=60&rend_all=1'

# SPLASH_LUA_SOURCE_LEETCODECN = '''
# function main(splash, args)
#   assert(splash:go(args.url))
#   assert(splash:wait(5))
#   local element = splash:select(".e1dj6frj0")
#   local bounds = element:bounds()
#   assert(element:mouse_hover{x=bounds.width, y=-3})

#   return splash:html()
# end
# '''

# remote splash service
REMOTE_SPLASH_API_ROOT = 'http://nuullll.com:8050/render.html'

USER_UPDATE_COOLDOWN = 600