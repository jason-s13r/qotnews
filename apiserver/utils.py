import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import commonmark
import random
import string

def gen_rand_id():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(4))

def render_md(md):
    if md:
        return commonmark.commonmark(md)
    else:
        return ''
