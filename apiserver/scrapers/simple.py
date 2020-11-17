import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests
from settings import READER_PORT

READ_API = 'http://127.0.0.1:{}/simple/details'.format(READER_PORT or 3000)
TIMEOUT = 20

def get_html(url):
    logging.info(f"Simple Scraper: {url}")
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
        logging.error('Problem getting article: {}'.format(str(e)))
        return None