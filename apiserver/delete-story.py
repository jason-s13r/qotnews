import database
import search
import sys

import json
import requests

database.init()
search.init()

def database_del_story(sid):
    try:
        session = database.Session()
        session.query(database.Story).filter(database.Story.sid==sid).delete()
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def search_del_story(sid):
    try:
        r = requests.delete(search.MEILI_URL + 'indexes/qotnews/documents/'+sid, timeout=2)
        if r.status_code != 202:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem deleting MeiliSearch story: {}'.format(str(e)))
        return False

if __name__ == '__main__':
    if len(sys.argv) == 2:
        sid = sys.argv[1]
    else:
        print('Usage: python delete-story.py [story id]')
        exit(1)

    story = database.get_story(sid)

    if story:
        print('Deleting story:')
        print(story.title)
        database_del_story(sid)
        search_del_story(sid)
        database.del_ref(story.ref)
    else:
        print('Story not found. Exiting.')
