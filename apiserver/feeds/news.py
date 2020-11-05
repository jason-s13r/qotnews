import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

import requests
from datetime import datetime
from bs4 import BeautifulSoup
from scrapers import declutter
import extruct
import pytz

from utils import clean

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'


def unix(date_str, tz=None):
    date_tzfix = date_str
    if ":" == date_tzfix[-3]:
        date_tzfix = date_tzfix[:-3]+date_tzfix[-2:]
    formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']
    formats = formats + [f.replace("T%H", " %H") for f in formats]
    for f in formats:
        try:
            dt = datetime.strptime(date_str, f)
            if tz:
                dt = pytz.timezone(tz).localize(dt)
            return int(dt.timestamp())
        except:
            pass
        try:
            dt = datetime.strptime(date_tzfix, f)
            if tz:
                dt = pytz.timezone(tz).localize(dt)
            return int(dt.timestamp())
        except:
            pass
    return 0


def xml(route, ref=None):
    try:
        headers = {'User-Agent': USER_AGENT, 'X-Forwarded-For': '66.249.66.1'}
        r = requests.get(route(ref), headers=headers, timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.text
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting URL: {}'.format(str(e)))
        return False


def parse_extruct(s, data):
    for rdfa in data['rdfa']:
            for key, props in rdfa.items():
                if 'http://ogp.me/ns#title' in props:
                    for values in props['http://ogp.me/ns#title']:
                        s['title'] = values['@value']
                if 'http://ogp.me/ns/article#modified_time' in props:
                    for values in props['http://ogp.me/ns/article#modified_time']:
                        s['date'] = values['@value']
                if 'http://ogp.me/ns/article#published_time' in props:
                    for values in props['http://ogp.me/ns/article#published_time']:
                        s['date'] = values['@value']

    for og in data['opengraph']:
        titles = list(filter(None, [value if 'og:title' in key else None for key, value in og['properties']]))
        modified = list(filter(None, [value if 'article:modified_time' in key else None for key, value in og['properties']]))
        published = list(filter(None, [value if 'article:published_time' in key else None for key, value in og['properties']]))
        if len(modified):
            s['date'] = modified[0]
        if len(published):
            s['date'] = published[0]
        if len(titles):
            s['title'] = titles[0]

    for md in data['microdata']:
        if md['type'] == 'https://schema.org/NewsArticle':
            props = md['properties']
            s['title'] = props['headline']
            if props['dateModified']:
                s['date'] = props['dateModified']
            if props['datePublished']:
                s['date'] = props['datePublished']
            if 'author' in props and props['author']:
                s['author'] = props['author']['properties']['name']

    for ld in data['json-ld']:
        if '@type' in ld and ld['@type'] in ['Article', 'NewsArticle']:
            s['title'] = ld['headline']
            if ld['dateModified']:
                s['date'] = ld['dateModified']
            if ld['datePublished']:
                s['date'] = ld['datePublished']
            if 'author' in ld and ld['author']:
                s['author'] = ld['author']['name']
        if '@graph' in ld:
            for gld in ld['@graph']:
                if '@type' in gld and gld['@type'] in ['Article', 'NewsArticle']:
                    s['title'] = gld['headline']
                    if gld['dateModified']:
                        s['date'] = gld['dateModified']
                    if gld['datePublished']:
                        s['date'] = gld['datePublished']

    return s

def comment(i):
    if 'author' not in i:
        return False

    c = {}
    c['author'] = i.get('author', '')
    c['score'] = i.get('points', 0)
    c['date'] = unix(i.get('date', 0))
    c['text'] = clean(i.get('text', '') or '')
    c['comments'] = [comment(j) for j in i['children']]
    c['comments'] = list(filter(bool, c['comments']))
    return c

def comment_count(i):
    alive = 1 if i['author'] else 0
    return sum([comment_count(c) for c in i['comments']]) + alive

class _Base:
    def __init__(url, tz=None):
        self.url = url
        self.tz = tz

    def feed(self, excludes=None):
        return []

    def story(self, ref):
        markup = xml(lambda x: ref)
        if not markup:
            return False

        s = {}
        s['author_link'] = ''
        s['score'] = 0
        s['comments'] = []
        s['num_comments'] = 0
        s['link'] = ref
        s['url'] = ref
        s['date'] = 0

        data = extruct.extract(markup)
        s = parse_extruct(s, data)
        if s['date']:
            s['date'] = unix(s['date'], tz=self.tz)

        if 'disqus' in markup:
            try:
                s['comments'] = declutter.get_comments(ref)
                c['comments'] = list(filter(bool, c['comments']))
                s['num_comments'] = comment_count(s['comments'])
            except KeyboardInterrupt:
                raise
            except:
                pass

        if not s['date']:
            return False
        return s

class Sitemap(_Base):
    def __init__(self, url, tz=None):
        self.tz = tz
        self.sitemap_url = url

    def feed(self, excludes=None):
        markup = xml(lambda x: self.sitemap_url)
        if not markup: return []
        soup = BeautifulSoup(markup, features='lxml')
        articles = soup.find('urlset').findAll('url')
        articles = list(filter(None, [a if a.find('lastmod') is not None else None for a in articles]))
        links = [x.find('loc').text for x in articles] or []
        links = list(set(links))
        if excludes:
            links = list(filter(None, [None if any(e in link for e in excludes) else link for link in links]))
        return links


class Category(_Base):
    def __init__(self, url, tz=None):
        self.tz = tz
        self.category_url = url
        self.base_url = '/'.join(url.split('/')[:3])

    def feed(self, excludes=None):
        markup = xml(lambda x: self.category_url)
        if not markup: return []
        soup = BeautifulSoup(markup, features='html.parser')
        links = soup.find_all('a', href=True)
        links = [link.get('href') for link in links]
        links = [f"{self.base_url}{link}" if link.startswith('/') else link for link in links]
        links = list(filter(None, [link if link.startswith(self.category_url) else None for link in links]))
        links = list(filter(None, [link if link != self.category_url else None for link in links]))
        links = list(set(links))
        if excludes:
            links = list(filter(None, [None if any(e in link for e in excludes) else link for link in links]))
        return links


# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    print("Sitemap: Stuff")
    site = Sitemap("https://www.stuff.co.nz/sitemap.xml")
    posts = site.feed()
    print(posts[:1])
    print(site.story(posts[0]))

    print("Category: RadioNZ Te Ao Māori")
    site = Category("https://www.rnz.co.nz/news/te-manu-korihi/")
    posts = site.feed()
    print(posts[:1])
    print(site.story(posts[0]))

    
