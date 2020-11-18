import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests

DECLUTTER_API = 'https://declutter.1j.nz/headless/details'
DECLUTTER_COMMENT_API = 'https://declutter.1j.nz/headless/comments'
TIMEOUT = 90


def get_html(url):
    logging.info(f"Declutter Scraper: {url}")
    details = get_details(url)
    if not details:
        return ''
    return details['content']

def get_details(url):
    try:
        r = requests.post(DECLUTTER_API, data=dict(url=url), timeout=TIMEOUT)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem decluttering article: {}'.format(str(e)))
        return None

def get_comments(url):
    try:
        r = requests.post(DECLUTTER_COMMENT_API, data=dict(url=url), timeout=TIMEOUT)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem getting comments for article: {}'.format(str(e)))
        return None