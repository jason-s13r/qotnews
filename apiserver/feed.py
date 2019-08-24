import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import requests

from feeds import hackernews

READ_API = 'http://127.0.0.1:33843'

def list():
    feed = []
    feed += [(x, 'hackernews') for x in hackernews.feed()]
    return feed

def get_article(url):
    try:
        r = requests.post(READ_API, data=dict(url=url), timeout=10)
        if r.status_code != 200:
            raise
        return r.text
    except BaseException as e:
        logging.error('Problem getting article: {}'.format(str(e)))
        return ''

def update_story(story):
    res = {}

    if story['source'] == 'hackernews':
        res = hackernews.story(story['ref'])
    else:
        return

    if res:
        story.update(res)
    if story.get('url', '') and not story.get('text', ''):
        if not story['url'].endswith('.pdf'):
            story['text'] = get_article(story['url'])
        else:
            story['text'] = '<p>Unsupported article type.</p>'
