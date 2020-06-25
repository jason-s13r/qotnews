import archive
import database
import json

database.init()
archive.init()

with archive.ix.searcher() as searcher:
    for docnum in searcher.document_numbers():
        try:
            print('docnum', docnum)
            res = searcher.stored_fields(docnum)
            print('id', res['id'])
            database.put(res['story'])
            print()
        except:
            print('skipping', docnum)
            pass
