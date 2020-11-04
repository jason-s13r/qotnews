import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests

DECLUTTER_API = 'https://declutter.1j.nz/details'


def get_html(url):
    try:
        logging.info(f"Declutter Scraper: {url}")
        details = get_details(url)
        return details['content']
    except:
        raise

def get_details(url):
    try:
        r = requests.post(DECLUTTER_API, data=dict(url=url), timeout=20)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem decluttering article: {}'.format(str(e)))
        return {}