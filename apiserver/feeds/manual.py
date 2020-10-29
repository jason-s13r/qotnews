import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests
import time
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'

def api(route):
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'X-Forwarded-For': '66.249.66.1',
        }
        r = requests.get(route, headers=headers, timeout=10)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.text
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting manual website: {}'.format(str(e)))
        return False

def story(ref):
    html = api(ref)
    if not html: return False

    soup = BeautifulSoup(html, features='html.parser')

    s = {}
    s['author'] = 'manual submission'
    s['author_link'] = 'https://news.t0.vc'
    s['score'] = 0
    s['date'] = int(time.time())
    s['title'] = str(soup.title.string) if soup.title else ref
    s['link'] = ref
    s['url'] = ref
    s['comments'] = []
    s['num_comments'] = 0

    return s

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    print(story('https://www.backblaze.com/blog/what-smart-stats-indicate-hard-drive-failures/'))
