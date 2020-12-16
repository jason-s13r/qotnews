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

def _update_current_story(story):
    logging.info('Updating story: {}'.format(str(story['ref'])))

    if story.get('url', ''):
        story['text'] = ''

    valid = feed.update_story(story, urlref=story['url'], is_manual=True)
    if valid:
        database.put_story(story)
        search.put_story(story)
    else:
        database.del_ref(story['ref'])
        logging.info('Removed ref {}'.format(story['ref']))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        sid = sys.argv[1]
    else:
        print('Usage: python delete-story.py [story id]')
        exit(1)

    story = database.get_story(sid).data
    if story:
        print('Updating story:')
        _update_current_story(story)
    else:
        print('Story not found. Exiting.')