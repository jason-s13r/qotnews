import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests
from settings import HEADLESS_READER_PORT

READ_API = 'http://127.0.0.1:{}/headless/details'.format(HEADLESS_READER_PORT or 33843)
READ_COMMENT__API = 'http://127.0.0.1:{}/headless/comments'.format(HEADLESS_READER_PORT or 33843)
TIMEOUT = 90

def get_html(url):
    logging.info(f"Headless Scraper: {url}")
    details = get_details(url)
    if not details:
        return ''
    return details['content']

def get_details(url):
    try:
        r = requests.post(READ_API, data=dict(url=url), timeout=TIMEOUT)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem scraping article: {}'.format(str(e)))
        return None

def get_comments(url):
    try:
        r = requests.post(READ_COMMENT_API, data=dict(url=url), timeout=TIMEOUT)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem getting comments for article: {}'.format(str(e)))
        return None
