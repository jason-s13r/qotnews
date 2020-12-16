import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
import requests

from settings import HEADLESS_READER_PORT, SIMPLE_READER_PORT

class Simple:
    def __init__(self, host, name, internal=True, timeout=90):
        self.host = host
        self.name = name
        self.internal = internal
        self.timeout = timeout
        self.variant = 'simple'

    def as_readable(self, details):
        if not self.internal:
            details['scraper_link'] = self.host
        return details

    def get_html(self, url):
        details = self.get_details(url)
        if not details:
            return ''
        return details['content']

    def get_details(self, url):
        logging.info(f"{self.name} Scraper: {url}")
        details = self._json(f"{self.host}/{self.variant}/details", dict(url=url), "article")
        if not details: return None
        return self.as_readable(details)


    def _json(self, url, data, adjective):
        try:
            r = requests.post(url, data=data, timeout=self.timeout)
            if r.status_code != 200:
                raise Exception('Bad response code ' + str(r.status_code))
            return r.json()
        except KeyboardInterrupt:
            raise
        except BaseException as e:
            logging.error('{}: Problem scraping {}: {}'.format(self.name, adjective, str(e)))
            return None


class Headless(Simple):
    def __init__(self, host, name, internal=True, timeout=90):
        self.host = host
        self.name = name
        self.internal = internal
        self.timeout = timeout
        self.variant = 'headless'

    def get_comments(self, url):
        logging.info(f"{self.name} Scraper: {url}")
        comments = self._json(f"{self.host}/{self.variant}/comments", dict(url=url), "comments")
        if not comments: return None
        return comments

declutter = Headless('https://declutter.1j.nz', 'Declutter', internal=False)
headless = Headless(f"http://127.0.0.1:{HEADLESS_READER_PORT or 33843}", 'Headless')
simple = Simple(f"http://127.0.0.1:{SIMPLE_READER_PORT or 33843}", 'Simple')