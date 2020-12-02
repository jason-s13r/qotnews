import re
from bs4 import BeautifulSoup

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

from misc.time import unix
from misc.api import xml
from utils import clean

def _soup_get_text(soup):
    if not soup: return None
    if soup.text: return soup.text

    s = soup.find(text=lambda tag: isinstance(tag, bs4.CData))
    if s and s.string: return s.string.strip()
    return None

def _parse_comment(soup):
    c = {
        'author': '',
        'authorLink': '',
        'score': 0,
        'date': 0,
        'text': '',
        'comments': [],
    }
    
    if soup.find('link'):
        title = _soup_get_text(soup.find('link'))
        if title and 'By:' in title:
            c['author'] = title.strip('By:').strip()
    if soup.find('dc:creator'):
        c['author'] = _soup_get_text(soup.find('dc:creator'))
    if soup.find('link'):
        c['authorLink'] = _soup_get_text(soup.find('link'))
    if soup.find('description'):
        c['text'] = clean(_soup_get_text(soup.find('description')))
    if soup.find('pubdate'):
        c['date'] = unix(soup.find('pubdate').text)
    elif soup.find('pubDate'):
        c['date'] = unix(soup.find('pubDate').text)

    return c

def get_comments(url):
    regex = r"https:\/\/www\.stuff\.co\.nz\/(.*\/\d+)/[^\/]+"
    p = re.compile(regex).match(url)
    path = p.groups()[0]
    comment_url = f'https://comments.us1.gigya.com/comments/rss/6201101/Stuff/stuff/{path}'
    markup = xml(lambda x: comment_url)
    if not markup: return []
    soup = BeautifulSoup(markup, features='html.parser')
    comments = soup.find_all('item')
    if not comments: return []
    comments = [_parse_comment(c) for c in comments]
    return comments


# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    comments = get_comments('https://www.stuff.co.nz/life-style/homed/houses/123418468/dear-jacinda-we-need-to-talk-about-housing')
    print(len(comments))
    print(comments[:5])