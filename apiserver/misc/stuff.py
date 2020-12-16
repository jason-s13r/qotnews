import re
from bs4 import BeautifulSoup

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

from misc.time import unix
from misc.api import xml, json
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

def _parse_json_comment(raw):
    c = {
        'author': '',
        'authorLink': '',
        'score': 0,
        'date': 0,
        'text': '',
        'comments': [],
    }

    sender = raw.get('sender', { 'name': '', 'profileURL': '' })
    c['author'] = sender.get('name', '')
    c['authorLink'] = sender.get('profileURL', '')
    c['score'] = raw.get('TotalVotes', 0)
    c['date'] = int(raw.get('timestamp', 0) / 1000)
    c['text'] = raw.get('commentText', '')
    c['comments'] = [_parse_json_comment(c) for c in raw.get('replies', [])]
    return c

def get_rss_comments(url):
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

def get_json_comments(url, markup=None):
    regex = r"https:\/\/www\.stuff\.co\.nz\/(.*\/\d+)/[^\/]+"
    p = re.compile(regex).match(url)
    if not p: return []
    path = p.groups()[0]
    if not markup:
        markup = xml(lambda x: url)
    soup = BeautifulSoup(markup, features='html.parser')
    scripts = soup.find_all('script', src=True)
    scripts = list(filter(None, [s if s['src'].startswith("https://cdns.gigya.com/JS/gigya.js?apiKey=") else None for s in scripts]))
    if not scripts: return []
    script = scripts[0]
    if not script: return []
    meh, params = script['src'].split('?', maxsplit=1)
    params = params.split('&')
    params = [p.split('=') for p in params]
    params = list(filter(None, [value if name.lower() == 'apikey' else None for name, value in params]))
    if not params: return []
    apiKey = params[0]
    if not apiKey: return []
    url = f"https://comments.us1.gigya.com/comments.getComments?threaded=true&format=json&categoryID=Stuff&streamID=stuff/{path}&APIKey={apiKey}"
    data = json(lambda x: url)
    comments = data.get('comments', [])
    comments = [_parse_json_comment(c) for c in comments]
    return comments



# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    #comments = get_json_comments('https://www.stuff.co.nz/life-style/homed/houses/123418468/dear-jacinda-we-need-to-talk-about-housing')
    comments = get_json_comments('https://www.stuff.co.nz/business/money/300174711/roll-back-minimum-wage-increases-nz-initiative-urges')
    print(len(comments))
    print(comments[:5])