from bs4 import BeautifulSoup

def get_icons(markup):
    soup = BeautifulSoup(markup, features='html.parser')
    icon32 = soup.find_all('link', rel="icon", href=True, sizes="32x32")
    icon16 = soup.find_all('link', rel="icon", href=True, sizes="16x16")
    favicon = soup.find_all('link', rel="shortcut icon", href=True)
    others = soup.find_all('link', rel="icon", href=True)
    icons = icon32 + icon16 + favicon + others
    base_url = '/'.join(urlref.split('/')[:3])
    icons = list(set([i.get('href') for i in icons]))
    icons = [i if i.startswith('http') else base_url + i for i in icons]

    return icons