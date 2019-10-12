import shelve

import archive

archive.init()

#with shelve.open('data/data') as db:
#    to_delete = []
#
#    for s in db.values():
#        if 'title' in s:
#            archive.update(s)
#        if 'id' in s:
#            to_delete.append(s['id'])
#
#    for id in to_delete:
#        del db[id]
#
#    for s in db['news_cache'].values():
#        if 'title' in s:
#            archive.update(s)

#with shelve.open('data/whoosh') as db:
#    for s in db['news_cache'].values():
#        if 'title' in s and not archive.get_story(s['id']):
#            archive.update(s)
