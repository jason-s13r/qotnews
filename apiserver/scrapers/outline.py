import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests

OUTLINE_REFERER = 'https://outline.com/'
OUTLINE_API = 'https://api.outline.com/v3/parse_article'
TIMEOUT = 20

name = 'Outline'

def get_html(url):
    details = get_details(url)
    if not details:
        return ''
    return details['content']

def get_details(url):
    outline = _get_outline(url)
    if not outline:
        return None
    return as_readable(outline)

def as_readable(details):
    readable = dict(details)
    readable.update({
        'byline': details['author'],
        'content': details['html'],
        'excerpt': _excerpt(details),
        'siteName': details['site_name'],
        'url': details['article_url'],
        'publisher': details['site_name'],
        'scraper_link': 'https://outline.com/' + details['short_code'],
    })
    return readable

def _get_outline(url):
    try:
        logging.info(f"Outline Scraper: {url}")
        params = {'source_url': url}
        headers = {'Referer': OUTLINE_REFERER}
        r = requests.get(OUTLINE_API, params=params, headers=headers, timeout=TIMEOUT)
        if r.status_code == 429:
            logging.info('Rate limited by outline, skipping...')
            return None
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
        return None

def _excerpt(details):
    meta = details.get('meta')
    if not meta: return ''
    if meta.get('description'): return meta.get('description', '')
    if not meta.get('og'): return ''
    return meta.get('og').get('og:description', '')