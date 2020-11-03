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
import extruct

from utils import clean

OUTLINE_API = 'https://api.outline.com/v3/parse_article'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'

def unix(date_str):
    date_tzfix = date_str
    if ":" == date_tzfix[-3]:
        date_tzfix = date_tzfix[:-3]+date_tzfix[-2:]
    formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']
    formats = formats + [f.replace("T%H", " %H") for f in formats]
    for f in formats:
        try:
            return int(datetime.strptime(date_str, f).timestamp())
        except:
            pass
        try:
            return int(datetime.strptime(date_tzfix, f).timestamp())
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
                        s['date'] = unix(values['@value'])
                if 'http://ogp.me/ns/article#published_time' in props:
                    for values in props['http://ogp.me/ns/article#published_time']:
                        s['date'] = unix(values['@value'])

    for og in data['opengraph']:
        titles = list(filter(None, [value if 'og:title' in key else None for key, value in og['properties']]))
        modified = list(filter(None, [value if 'article:modified_time' in key else None for key, value in og['properties']]))
        published = list(filter(None, [value if 'article:published_time' in key else None for key, value in og['properties']]))
        if len(modified):
            s['date'] = unix(modified[0])
        if len(published):
            s['date'] = unix(published[0])
            s['date'] = unix(published[0] or modified[0] or '')
        if len(titles):
            s['title'] = titles[0]

    for md in data['microdata']:
        if md['type'] == 'https://schema.org/NewsArticle':
            props = md['properties']
            s['title'] = props['headline']
            if props['dateModified']:
                s['date'] = unix(props['dateModified'])
            if props['datePublished']:
                s['date'] = unix(props['datePublished'])
            if 'author' in props and props['author']:
                s['author'] = props['author']['properties']['name']

    for ld in data['json-ld']:
        if ld['@type'] == 'Article':
            s['title'] = ld['headline']
            if ld['dateModified']:
                s['date'] = unix(ld['dateModified'])
            if ld['datePublished']:
                s['date'] = unix(ld['datePublished'])
            if 'author' in ld and ld['author']:
                s['author'] = ld['author']['name']

    return s

class Sitemap:
    def __init__(self, url):
        self.sitemap_url = url

    def feed(self):
        markup = xml(lambda x: self.sitemap_url)
        if not markup: return []
        soup = BeautifulSoup(markup, features='lxml')
        articles = soup.find('urlset').findAll('url')
        articles = list(filter(None, [a if a.find('lastmod') is not None else None for a in articles]))
        return [x.find('loc').text for x in articles] or []

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
        return s

class Category:
    def __init__(self, url):
        self.category_url = url
        self.base_url = '/'.join(url.split('/')[:3])

    def feed(self):
        markup = xml(lambda x: self.category_url)
        if not markup: return []
        soup = BeautifulSoup(markup, features='html.parser')
        links = soup.find_all('a', href=True)
        links = [link.get('href') for link in links]
        links = [f"{self.base_url}{link}" if link.startswith('/') else link for link in links]
        links = list(filter(None, [link if link.startswith(self.category_url) else None for link in links]))
        return links

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
        return s

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    print("Sitemap: Stuff")
    site = Sitemap("https://www.stuff.co.nz/sitemap.xml")
    posts = site.feed()
    print(posts[:1])
    print(site.story(posts[0]))

    print("Sitemap: NZ Herald")
    site = Sitemap("https://www.nzherald.co.nz/arcio/news-sitemap/")
    posts = site.feed()
    print(posts[:1])
    print(site.story(posts[0]))

    print("Category: RadioNZ Te Ao Māori")
    site = Category("https://www.rnz.co.nz/news/te-manu-korihi/")
    posts = site.feed()
    print(posts[:1])
    print(site.story(posts[0]))
    print("Category: Newsroom Business")
    site = Category("https://www.newsroom.co.nz/business/")
    posts = site.feed()
    print(posts[:1])
    print(site.story(posts[0]))