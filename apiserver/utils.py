import logging
logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import commonmark
import random
import string

from bleach.sanitizer import Cleaner

def gen_rand_id():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(4))

def render_md(md):
    if md:
        return commonmark.commonmark(md)
    else:
        return ''

ALLOWED_TAGS = [
        'a',
        'abbr',
        'acronym',
        'b',
        'blockquote',
        'code',
        'em',
        'i',
        'li',
        'ol',
        'strong',
        'ul',
        'p',
        'hr',
        'small',
        'ins',
        'sup',
        'sub',
        'details',
        'summary',
        'br',
        'pre',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'h6',
        'table',
        'thead',
        'tr',
        'th',
        'td',
        'tbody',
        ]

clean = Cleaner(tags=ALLOWED_TAGS).clean
