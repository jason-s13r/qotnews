import archive
import database
import json

database.init()
archive.init()

with archive.ix.searcher() as searcher:
    for docnum in searcher.document_numbers():
        try:
            #if docnum > 500:
            #    break

            print('docnum', docnum)
            res = searcher.stored_fields(docnum)
            print('id', res['id'])
            database.put_story(res['story'])
            print()
        except BaseException as e:
            print('skipping', docnum)
            print('reason:', e)
