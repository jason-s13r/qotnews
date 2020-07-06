import archive
import database
import search

import json
import requests

database.init()
archive.init()
search.init()

count = 0

def database_del_story_by_ref(ref):
    try:
        session = database.Session()
        session.query(database.Story).filter(database.Story.ref==ref).delete()
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

with archive.ix.searcher() as searcher:
    print('count all', searcher.doc_count_all())
    print('count', searcher.doc_count())

    for doc in searcher.documents():
        try:
            print('num', count, 'id', doc['id'])
            count += 1

            story = doc['story']
            story.pop('img', None)

            if 'reddit.com/r/technology' in story['link']:
                print('skipping r/technology')
                continue

            try:
                database.put_story(story)
            except database.IntegrityError:
                print('collision!')
                old_story = database.get_story_by_ref(story['ref'])
                old_story = json.loads(old_story.full_json)
                if story['num_comments'] > old_story['num_comments']:
                    print('more comments, replacing')
                    database_del_story_by_ref(story['ref'])
                    database.put_story(story)
                    search_del_story(old_story['id'])
                else:
                    print('fewer comments, skipping')
                    continue

            search.put_story(story)
            print()
        except KeyboardInterrupt:
            break
        except BaseException as e:
            print('skipping', doc['id'])
            print('reason:', e)
