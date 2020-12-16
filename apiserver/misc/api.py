import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests

GOOGLEBOT_USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
GOOGLEBOT_IP = '66.249.66.1'
TIMEOUT = 30

def request(route, ref=None, headers=dict(), use_googlebot=True, attempt=0):
    original = dict(headers)
    headers = dict(headers)
    try:
        if use_googlebot:
            headers['User-Agent'] = GOOGLEBOT_USER_AGENT
            headers['X-Forwarded-For'] = GOOGLEBOT_IP
        r = requests.get(route(ref), headers=headers, timeout=TIMEOUT)
        if r.status_code != 200:
            if attempt == 0:
                return request(route, ref, original, not use_googlebot, 1)
            raise Exception('Bad response code ' + str(r.status_code))
        return r
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting URL: {}'.format(str(e)))
        return False

def xml(route, ref=None, headers=dict(), use_googlebot=True):
    r = request(route, ref, headers, use_googlebot)
    if not r: return False
    return r.text
    

def json(route, ref=None, headers=dict(), use_googlebot=True):
    r = request(route, ref, headers, use_googlebot)
    if not r: return False
    return r.json()