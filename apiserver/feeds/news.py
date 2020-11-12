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
import dateutil.parser
import extruct
import pytz

from utils import clean
import settings

tzinfos = {
    'NZDT': pytz.timezone('Pacific/Auckland'),
    'NZST': pytz.timezone('Pacific/Auckland')
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'
#USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

def unix(date_str, tz=None):
    try:
        dt = dateutil.parser.parse(date_str, tzinfos=tzinfos)
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
    rdfa_keys = {
        'title': [
            'http://ogp.me/ns#title',
            'https://ogp.me/ns#title',
        ],
        'date': [
            'http://ogp.me/ns/article#modified_time',
            'https://ogp.me/ns/article#modified_time',
            'http://ogp.me/ns/article#published_time',
            'https://ogp.me/ns/article#published_time',
        ]
    }
    for rdfa in data['rdfa']:
        for key, props in rdfa.items():
            for attribute, properties in rdfa_keys.items():
                for prop in properties:
                    if prop in props:
                        for values in props[prop]:
                            s[attribute] = values['@value']

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
        if md['type'] in ['https://schema.org/NewsArticle', 'http://schema.org/NewsArticle']:
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
                if 'name' in ld['author']:
                    s['author'] = ld['author']['name']
                elif len(ld['author']):
                    s['author'] = ld['author'][0]['name']
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

        soup = BeautifulSoup(markup, features='html.parser')
        icon32 = soup.find_all('link', rel="icon", href=True, sizes="32x32")
        icon16 = soup.find_all('link', rel="icon", href=True, sizes="16x16")
        favicon = soup.find_all('link', rel="shortcut icon", href=True)
        others = soup.find_all('link', rel="icon", href=True)
        icons = icon32 + icon16 + favicon + others
        base_url = '/'.join(ref.split('/')[:3])
        icons = list(set([i.get('href') for i in icons]))
        icons = [i if i.startswith('http') else base_url + i for i in icons]

        if icons:
            s['icon'] = icons[0]

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

def get_sitemap_date(a):
    if a.find('lastmod'):
        return a.find('lastmod').text
    if a.find('news:publication_date'):
        return a.find('news:publication_date').text
    if a.find('ns2:publication_date'):
        return a.find('ns2:publication_date').text
    return ''

class Sitemap(_Base):
    def __init__(self, url, tz=None):
        self.tz = tz
        self.sitemap_url = url

    def feed(self, excludes=None):
        links = []
        if isinstance(self.sitemap_url, str):
            links += self._get_sitemap(self.sitemap_url, excludes)
        elif isinstance(self.sitemap_url, list):
            for url in self.sitemap_url:
                links += self._get_sitemap(url, excludes)
        return list(set(links))

    def _filter_links(self, links, excludes=None):
        too_old = datetime.now().timestamp() - settings.MAX_STORY_AGE
        links = list(filter(None, [a if get_sitemap_date(a) else None for a in links]))
        links = list(filter(None, [a if unix(get_sitemap_date(a)) > too_old else None for a in links]))
        links.sort(key=lambda a: unix(get_sitemap_date(a)), reverse=True)

        links = [x.find('loc').text for x in links] or []
        links = list(set(links))
        if excludes:
            links = list(filter(None, [None if any(e in link for e in excludes) else link for link in links]))
        return links

    def _get_sitemap(self, feed_url, excludes=None):
        markup = xml(lambda x: feed_url)
        if not markup: return []
        soup = BeautifulSoup(markup, features='lxml')
        links = []
        feed_urls = []
        if soup.find('sitemapindex'):
            sitemap = soup.find('sitemapindex').findAll('sitemap')
            feed_urls = list(filter(None, [a if a.find('loc') else None for a in sitemap]))
        if soup.find('urlset'):
            sitemap = soup.find('urlset').findAll('url')
            links = list(filter(None, [a if a.find('loc') else None for a in sitemap]))

        feed_urls = self._filter_links(feed_urls, excludes)
        links = self._filter_links(links, excludes)

        for url in feed_urls:
            links += self._get_sitemap(url, excludes)
        return list(set(links))

class Category(_Base):
    def __init__(self, url, tz=None):
        self.tz = tz
        self.category_url = url

    def _filter_links(self, links, category_url, excludes=None):
        links = list(filter(None, [link if link.startswith(category_url) else None for link in links]))
        links = list(filter(None, [link if link != category_url else None for link in links]))
        links = list(set(links))
        if excludes:
            links = list(filter(None, [None if any(e in link for e in excludes) else link for link in links]))
        return links

    def _get_category(self, category_url, excludes=None):
        base_url = '/'.join(category_url.split('/')[:3])
        markup = xml(lambda x: category_url)
        if not markup: return []
        soup = BeautifulSoup(markup, features='html.parser')
        links = soup.find_all('a', href=True)
        links = [link.get('href') for link in links]
        links = [f"{base_url}{link}" if link.startswith('/') else link for link in links]
        links = self._filter_links(links, category_url, excludes)
        return links

    def feed(self, excludes=None):
        links = []
        if isinstance(self.category_url, str):
            links += self._get_category(self.category_url, excludes)
        elif isinstance(self.category_url, list):
            for url in self.category_url:
                links += self._get_category(url, excludes)
        return list(set(links))


# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    print("Sitemap: The Spinoff")
    site = Sitemap("https://thespinoff.co.nz/sitemap.xml")
    excludes = [
        'thespinoff.co.nz/sitemap-misc.xml',
        'thespinoff.co.nz/sitemap-authors.xml',
        'thespinoff.co.nz/sitemap-tax-category.xml',
    ]
    posts = site.feed(excludes)
    print(posts[:5])
    print(site.story(posts[0]))

    print("Sitemap: Newshub")
    site = Sitemap([
        'https://www.newshub.co.nz/home/politics.gnewssitemap.xml',
        'https://www.newshub.co.nz/home/new-zealand.gnewssitemap.xml',
        'https://www.newshub.co.nz/home/world.gnewssitemap.xml',
        'https://www.newshub.co.nz/home/money.gnewssitemap.xml',
    ])
    posts = site.feed()
    print(posts[:5])
    print(site.story(posts[0]))
    print(site.story(posts[:-1]))

