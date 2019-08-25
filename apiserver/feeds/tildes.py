import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import requests
from bs4 import BeautifulSoup
from datetime import datetime

USER_AGENT = 'qotnews scraper (github:tannercollin)'

API_TOPSTORIES = lambda x: 'https://tildes.net'
API_ITEM = lambda x : 'https://tildes.net/~qotnews/{}/'.format(x)

SITE_LINK = lambda x : 'https://tildes.net/~qotnews/{}/'.format(x)
SITE_AUTHOR_LINK = lambda x : 'https://tildes.net/user/{}'.format(x)

def api(route, ref=None):
    try:
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(route(ref), headers=headers, timeout=5)
        if r.status_code != 200:
            raise
        return r.text
    except BaseException as e:
        logging.error('Problem hitting tildes website: {}'.format(str(e)))
        return False

def feed():
    soup = BeautifulSoup(api(API_TOPSTORIES), features='html.parser')
    articles = soup.find('ol', class_='topic-listing').findAll('article')
    return [x['id'].split('-')[1] for x in articles][:30] or []

def unix(date_str):
    return int(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').timestamp())

def comment(i):
    i = i.article
    c = {}
    c['author'] = str(i.find('a', class_='link-user').string)
    c['score'] = 1
    c['date'] = unix(i.find('time')['datetime'])
    c['text'] = i.find('div', class_='comment-text').encode_contents().decode()
    c['comments'] = [comment(j) for j in i.find('ol', class_='comment-tree').findAll('li', recursive=False)] if i.ol else []
    return c

def story(ref):
    html = api(API_ITEM, ref)
    if not html: return False

    soup = BeautifulSoup(html, features='html.parser')
    a = soup.find('article', class_='topic-full')
    h = a.find('header')

    s = {}
    s['author'] = str(h.find('a', class_='link-user').string)
    s['author_link'] = SITE_AUTHOR_LINK(s['author'])
    s['score'] = int(h.find('span', class_='topic-voting-votes').string)
    s['date'] = unix(h.find('time')['datetime'])
    s['title'] = str(h.h1.string)
    s['link'] = SITE_LINK(ref)
    ud = a.find('div', class_='topic-full-link')
    s['url'] = ud.a['href'] if ud else s['link']
    s['comments'] = [comment(i) for i in a.find('ol', id='comments').findAll('li', recursive=False)]
    ch = a.find('header', class_='topic-comments-header')
    s['num_comments'] = int(ch.h2.string.split(' ')[0]) if ch else 0

    td = a.find('div', class_='topic-full-text')
    if td:
        s['text'] = td.encode_contents().decode()

    return s

if __name__ == '__main__':
    print(feed())
    normal = story('gxt')
    print(normal)
    no_comments = story('gxr')
    print(no_comments)
    self_post = story('gsb')
    print(self_post)

    # make sure there's no self-reference
    import copy
    for x in [normal, no_comments, self_post]:
        _ = copy.deepcopy(x)
