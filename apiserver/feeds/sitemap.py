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
    return int(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').timestamp())

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

def get_article_details(url):
    try:
        params = {'source_url': url}
        headers = {'Referer': 'https://outline.com/'}
        r = requests.get(OUTLINE_API, params=params, headers=headers, timeout=20)
        if r.status_code == 429:
            logging.info('Rate limited by outline, sleeping 30s and skipping...')
            time.sleep(30)
            return ''
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        data = r.json()['data']
        if 'URL is not supported by Outline' in data['html']:
            raise Exception('URL not supported by Outline')
        return (data, "outline")
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem outlining article: {}'.format(str(e)))
        return (None, None)


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
        markup = xml(lambda x: self.sitemap_url)
        if not markup: return []
        soup = BeautifulSoup(markup, features='lxml')
        articles = soup.find('urlset').findAll('url')
        articles = list(filter(None, [a if a.find('lastmod') is not None else None for a in articles]))
        articles = list(filter(None, [a if a.find('loc').text == ref else None for a in articles]))

        if len(articles) == 0:
            return False

        r = articles[0]
        if not r:
            return False

        html = xml(lambda x: ref)

        if not html:
            return False

        data = extruct.extract(html)

        s = {}
        s['author_link'] = ''
        s['score'] = ''
        s['comments'] = []
        s['num_comments'] = 0
        s['link'] = ref
        s['url'] = ref
        s['date'] = unix(r.find('lastmod').text)

        for og in data['opengraph']:
           titles = list(filter(None, [value if 'og:title' in key else None for key, value in og['properties']]))
           if len(titles):
               s['title'] = titles[0]


        for md in data['microdata']:
            if md['type'] == 'https://schema.org/NewsArticle':
                props = md['properties']
                s['title'] = props['headline']
                if props['author']:
                    s['author'] = props['author']['properties']['name']

        for ld in data['json-ld']:
            if ld['@type'] == 'Article':
                s['title'] = ld['headline']
                if ld['author']:
                    s['author'] = ld['author']['name']
        return s


# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    # site = Sitemap("https://www.stuff.co.nz/sitemap.xml")
    site = Sitemap("https://www.nzherald.co.nz/arcio/news-sitemap/")
    posts = site.feed()
    print(posts[:1])
    print(site.story(posts[0]))
