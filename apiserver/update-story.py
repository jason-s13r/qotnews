import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import sys
import json
import requests

import database
import feed
import search

database.init()
search.init()

def _update_current_story(story, item):
    logging.info('Updating story: {}'.format(str(story['ref'])))

    if story.get('url', ''):
        story['text'] = ''

    valid = feed.update_story(story, urlref=item['urlref'])
    if valid:
        database.put_story(story)
        search.put_story(story)
    else:
        database.del_ref(item['ref'])
        logging.info('Removed ref {}'.format(item['ref']))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        sid = sys.argv[1]
    else:
        print('Usage: python delete-story.py [story id]')
        exit(1)

    item = database.get_ref_by_sid(sid)

    if item:
        story = database.get_story(item['sid']).data
        if story:
            print('Updating story:')
            _update_current_story(story, item)
        else:
            print('Story not found. Exiting.')
    else:
        print('Story not found. Exiting.')