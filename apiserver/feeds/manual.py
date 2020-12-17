import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

from misc.news import Base

class Manual(Base):
    refs = []

    def add_links(self, link):
        if isinstance(link, str):
            self.refs += [link]
        elif isinstance(link, list):
            self.refs += link

    def feed(self):
        ref = self.refs
        self.refs = []
        return ref

    def story(self, ref):
        s = super().story(ref, ref, is_manual=True)
        if not s: return False
        if not s['title']: return False
        if not s['author']:
            s['author'] = '[manual submission]'
        if not s['date']:
            s['date'] = datetime.now().timestamp()
        return s

manual = Manual()

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    story = manual.story('https://www.backblaze.com/blog/what-smart-stats-indicate-hard-drive-failures/')
    print(story)
