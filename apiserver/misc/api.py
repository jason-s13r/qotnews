import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests

USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
FORWARD_IP = '66.249.66.1'

def xml(route, ref=None):
    try:
        headers = {'User-Agent': USER_AGENT, 'X-Forwarded-For': FORWARD_IP}
        r = requests.get(route(ref), headers=headers, timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.text
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting URL: {}'.format(str(e)))
        return False

def json(route, ref=None):
    try:
        headers = {'User-Agent': USER_AGENT, 'X-Forwarded-For': FORWARD_IP}
        r = requests.get(route(ref), headers=headers, timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting URL: {}'.format(str(e)))
        return False