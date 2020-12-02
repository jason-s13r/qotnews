import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests

MEILI_URL = 'http://127.0.0.1:7700/'

def create_index():
    try:
        json = dict(name='qotnews', uid='qotnews')
        r = requests.post(MEILI_URL + 'indexes', json=json, timeout=2)
        if r.status_code != 201:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem creating MeiliSearch index: {}'.format(str(e)))
        return False

def update_rankings():
    try:
        json = ['typo', 'words', 'proximity', 'attribute', 'desc(date)', 'wordsPosition', 'exactness']
        r = requests.post(MEILI_URL + 'indexes/qotnews/settings/ranking-rules', json=json, timeout=2)
        if r.status_code != 202:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem setting MeiliSearch ranking rules: {}'.format(str(e)))
        return False

def update_attributes():
    try:
        json = ['title', 'url', 'author', 'link', 'id', 'source']
        r = requests.post(MEILI_URL + 'indexes/qotnews/settings/searchable-attributes', json=json, timeout=2)
        if r.status_code != 202:
            raise Exception('Bad response code ' + str(r.status_code))
        requests.delete(MEILI_URL + 'indexes/qotnews/settings/displayed-attributes', timeout=2)
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem setting MeiliSearch searchable attributes: {}'.format(str(e)))
        return False

def init():
    create_index()
    update_rankings()
    update_attributes()

def put_story(story):
    story = story.copy()
    story.pop('text', None)
    story.pop('comments', None)
    try:
        r = requests.post(MEILI_URL + 'indexes/qotnews/documents', json=[story], timeout=2)
        if r.status_code != 202:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem putting MeiliSearch story: {}'.format(str(e)))
        return False

def search(q, skip=0, limit=250):
    try:
        params = dict(q=q, skip=skip, limit=limit)
        r = requests.get(MEILI_URL + 'indexes/qotnews/search', params=params, timeout=2)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()['hits']
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem searching MeiliSearch: {}'.format(str(e)))
        return False
    
if __name__ == '__main__':
    create_index()

    print(search('the'))
