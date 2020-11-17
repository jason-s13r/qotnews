import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests

READ_API = 'http://127.0.0.1:33843/headless/details'
READ_COMMENT__API = 'http://127.0.0.1:33843/headless/comments'
TIMEOUT = 60


def get_html(url):
    logging.info(f"Headless Browser Scraper: {url}")
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
