import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests
import time

from feeds import hackernews, reddit, tildes

OUTLINE_API = 'https://outlineapi.com/article'
READ_API = 'http://127.0.0.1:33843'

def list():
    feed = []
    feed += [(x, 'hackernews') for x in hackernews.feed()[:10]]
    feed += [(x, 'reddit') for x in reddit.feed()[:5]]
    feed += [(x, 'tildes') for x in tildes.feed()[:5]]
    return feed

def get_article(url):
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
    else:
        return

    if res:
        story.update(res)
    if story.get('url', '') and not story.get('text', ''):
        if not story['url'].endswith('.pdf'):
            logging.info('Getting article ' + story['url'])
            story['text'] = get_article(story['url'])
        else:
            story['text'] = '<p>Unsupported article type.</p>'

if __name__ == '__main__':
    test_news_cache = {}
    nid = 'jean'
    ref = 20802050
    source = 'hackernews'
    test_news_cache[nid] = dict(id=nid, ref=ref, source=source)
    news_story = test_news_cache[nid]
    update_story(news_story)
    print('done')
