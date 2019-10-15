import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests
from bs4 import BeautifulSoup
from datetime import datetime

# cache the topic groups to prevent redirects
group_lookup = {}

USER_AGENT = 'qotnews scraper (github:tannercollin)'

API_TOPSTORIES = lambda : 'https://tildes.net'
API_ITEM = lambda x : 'https://tildes.net/shortener/{}'.format(x)

SITE_LINK = lambda group, ref : 'https://tildes.net/{}/{}'.format(group, ref)
SITE_AUTHOR_LINK = lambda x : 'https://tildes.net/user/{}'.format(x)

def api(route):
    try:
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(route, headers=headers, timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.text
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting tildes website: {}'.format(str(e)))
        return False

def feed():
    html = api(API_TOPSTORIES())
    if not html: return []
    soup = BeautifulSoup(html, features='html.parser')
    articles = soup.find('ol', class_='topic-listing').findAll('article')
    return [x['id'].split('-')[1] for x in articles] or []

def unix(date_str):
    return int(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').timestamp())

def comment(i):
    i = i.article

    if i.find('div', class_='is-comment-removed'):
        return False

    c = {}
    lu = i.find('a', class_='link-user')
    c['author'] = str(lu.string if lu else 'unknown user')
    c['score'] = 1
    c['date'] = unix(i.find('time')['datetime'])
    c['text'] = i.find('div', class_='comment-text').encode_contents().decode()
    ct = i.find('ol', class_='comment-tree')
    c['comments'] = [comment(j) for j in ct.findAll('li', recursive=False)] if ct else []
    c['comments'] = list(filter(bool, c['comments']))
    return c

def story(ref):
    if ref in group_lookup:
        html = api(SITE_LINK(group_lookup[ref], ref))
    else:
        html = api(API_ITEM(ref))
    if not html: return False

    soup = BeautifulSoup(html, features='html.parser')
    a = soup.find('article', class_='topic-full')
    h = a.find('header')
    lu = h.find('a', class_='link-user')

    error = a.find('div', class_='text-error')
    if error:
        if 'deleted' in error.string or 'removed' in error.string:
            return False

    s = {}
    s['author'] = str(lu.string if lu else 'unknown user')
    s['author_link'] = SITE_AUTHOR_LINK(s['author'])
    s['score'] = int(h.find('span', class_='topic-voting-votes').string)
    s['date'] = unix(h.find('time')['datetime'])
    s['title'] = str(h.h1.string)
    s['group'] = str(soup.find('a', class_='site-header-context').string)
    group_lookup[ref] = s['group']
    s['link'] = SITE_LINK(s['group'], ref)
    ud = a.find('div', class_='topic-full-link')
    s['url'] = ud.a['href'] if ud else s['link']
    sc = a.find('ol', id='comments')
    s['comments'] = [comment(i) for i in sc.findAll('li', recursive=False)]
    s['comments'] = list(filter(bool, s['comments']))
    ch = a.find('header', class_='topic-comments-header')
    s['num_comments'] = int(ch.h2.string.split(' ')[0]) if ch else 0

    if s['score'] < 8 and s['num_comments'] < 6:
        return False

    td = a.find('div', class_='topic-full-text')
    if td:
        s['text'] = td.encode_contents().decode()

    return s

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    #print(feed())
    #normal = story('gxt')
    #print(normal)
    #no_comments = story('gxr')
    #print(no_comments)
    #self_post = story('gsb')
    #print(self_post)
    #li_comment = story('gqx')
    #print(li_comment)
    broken = story('hsg')
    print(broken)

    # make sure there's no self-reference
    #import copy
    #for x in [normal, no_comments, self_post, li_comment]:
    #    _ = copy.deepcopy(x)
