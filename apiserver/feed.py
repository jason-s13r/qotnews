import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests
import time

from feeds import hackernews, reddit, tildes

OUTLINE_API = 'https://outlineapi.com/article'
ARCHIVE_API = 'https://archive.fo/submit/'
READ_API = 'http://127.0.0.1:33843'

INVALID_FILES = ['.pdf', '.png', '.jpg', '.gif']
INVALID_DOMAINS = ['youtube.com']

def list():
    feed = []
    feed += [(x, 'hackernews') for x in hackernews.feed()[:10]]
    feed += [(x, 'reddit') for x in reddit.feed()[:10]]
    feed += [(x, 'tildes') for x in tildes.feed()[:10]]
    return feed

def get_article(url):
    if 'bloomberg.com' in url:
        try:
            logging.info('Article from Bloomberg, archiving first...')
            data = {'submitid': '9tjtS1EYe5wy8AJiYgVfH9P97uHU1IHG4lO67hsQpHOC3KKJrhqVIoQG2U7Rg%2Fpr', 'url': url}
            r = requests.post(ARCHIVE_API, data=data, timeout=20, allow_redirects=False)
            if r.status_code == 200:
                logging.error('Submitted for archiving. Skipping to wait...')
                return ''
            elif 'location' in r.headers:
                url = r.headers['location']
            else:
                raise Exception('Bad response code ' + str(r.status_code))
        except BaseException as e:
            logging.error('Problem archiving article: {}'.format(str(e)))
            return ''

    try:
        params = {'source_url': url}
        headers = {'Referer': 'https://outline.com/'}
        r = requests.get(OUTLINE_API, params=params, headers=headers, timeout=20)
        if r.status_code == 429:
            logging.error('Rate limited by outline, sleeping 30s and skipping...')
            time.sleep(30)
            return ''
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        html = r.json()['data']['html']
        if 'URL is not supported by Outline' in html:
            raise Exception('URL not supported by Outline')
        return html
    except BaseException as e:
        logging.error('Problem outlining article: {}'.format(str(e)))

    logging.info('Trying our server instead...')

    try:
        r = requests.post(READ_API, data=dict(url=url), timeout=10)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.text
    except BaseException as e:
        logging.error('Problem getting article: {}'.format(str(e)))
        return ''

def update_story(story):
    res = {}

    logging.info('Updating story ' + str(story['ref']))

    if story['source'] == 'hackernews':
        res = hackernews.story(story['ref'])
    elif story['source'] == 'reddit':
        res = reddit.story(story['ref'])
    elif story['source'] == 'tildes':
        res = tildes.story(story['ref'])

    if res:
        story.update(res) # join dicts
    else:
        logging.info('Article not ready yet')
        return False

    if story.get('url', '') and not story.get('text', ''):
        for ext in INVALID_FILES:
            if story['url'].endswith(ext):
                logging.info('URL invalid file type ({})'.format(ext))
                return False

        for domain in INVALID_DOMAINS:
            if domain in story['url']:
                logging.info('URL invalid domain ({})'.format(domain))
                return False

        logging.info('Getting article ' + story['url'])
        story['text'] = get_article(story['url'])
        if not story['text']: return False

    return True

if __name__ == '__main__':
    #test_news_cache = {}
    #nid = 'jean'
    #ref = 20802050
    #source = 'hackernews'
    #test_news_cache[nid] = dict(id=nid, ref=ref, source=source)
    #news_story = test_news_cache[nid]
    #update_story(news_story)

    print(get_article('https://www.bloomberg.com/news/articles/2019-09-23/xi-s-communists-under-pressure-as-high-prices-hit-china-workers'))

    print('done')
