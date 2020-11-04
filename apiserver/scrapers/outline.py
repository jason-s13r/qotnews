import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests

OUTLINE_REFERER = 'https://outline.com/'
OUTLINE_API = 'https://api.outline.com/v3/parse_article'


def get_html(url):
    try:
        details = get_details(url)
        return details['html']
    except:
        raise

def get_details(url):
    try:
        logging.info(f"Outline Scraper: {url}")
        params = {'source_url': url}
        headers = {'Referer': OUTLINE_REFERER}
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
        return data
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem outlining article: {}'.format(str(e)))
        return {}