
from bs4 import BeautifulSoup

def get_icons(markup, url):
    soup = BeautifulSoup(markup, features='html.parser')
    icon32 = soup.find_all('link', rel="icon", href=True, sizes="32x32")
    icon16 = soup.find_all('link', rel="icon", href=True, sizes="16x16")
    favicon = soup.find_all('link', rel="shortcut icon", href=True)
    others = soup.find_all('link', rel="icon", href=True)
    icons = icon32 + icon16 + favicon + others
    base_url = '/'.join(url.split('/')[:3])
    icons = list(set([i.get('href') for i in icons]))
    icons = [i if i.startswith('http') else base_url + i for i in icons]

    return icons

def parse_extruct(s, data):
    rdfa_keys = {
        'title': [
            'http://ogp.me/ns#title',
            'https://ogp.me/ns#title',
        ],
        'date': [
            'http://ogp.me/ns/article#modified_time',
            'https://ogp.me/ns/article#modified_time',
            'http://ogp.me/ns/article#published_time',
            'https://ogp.me/ns/article#published_time',
        ]
    }
    for rdfa in data['rdfa']:
        for key, props in rdfa.items():
            for attribute, properties in rdfa_keys.items():
                for prop in properties:
                    if prop in props:
                        for values in props[prop]:
                            s[attribute] = values['@value']

    for og in data['opengraph']:
        titles = list(filter(None, [value if 'og:title' in key else None for key, value in og['properties']]))
        modified = list(filter(None, [value if 'article:modified_time' in key else None for key, value in og['properties']]))
        published = list(filter(None, [value if 'article:published_time' in key else None for key, value in og['properties']]))
        if len(modified):
            s['date'] = modified[0]
        if len(published):
            s['date'] = published[0]
        if len(titles):
            s['title'] = titles[0]

    for md in data['microdata']:
        if md['type'] in ['https://schema.org/NewsArticle', 'http://schema.org/NewsArticle']:
            props = md['properties']
            s['title'] = props['headline']
            if props['dateModified']:
                s['date'] = props['dateModified']
            if props['datePublished']:
                s['date'] = props['datePublished']
            if 'author' in props and props['author']:
                if 'properties' in props['author']:
                    s['author'] = props['author']['properties']['name']
                elif isinstance(props['author'], list):
                    s['author'] = props['author'][0]['properties']['name']

    for ld in data['json-ld']:
        if '@type' in ld and ld['@type'] in ['Article', 'NewsArticle']:
            s['title'] = ld['headline']
            if ld['dateModified']:
                s['date'] = ld['dateModified']
            if ld['datePublished']:
                s['date'] = ld['datePublished']
            if 'author' in ld and ld['author']:
                if 'name' in ld['author']:
                    s['author'] = ld['author']['name']
                elif isinstance(ld['author'], list):
                    s['author'] = ld['author'][0]['name']
        if '@graph' in ld:
            for gld in ld['@graph']:
                if '@type' in gld and gld['@type'] in ['Article', 'NewsArticle']:
                    s['title'] = gld['headline']
                    if gld['dateModified']:
                        s['date'] = gld['dateModified']
                    if gld['datePublished']:
                        s['date'] = gld['datePublished']

    return s