from whoosh.analysis import StemmingAnalyzer, CharsetFilter, NgramFilter
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.support.charset import accent_map

analyzer = StemmingAnalyzer() | CharsetFilter(accent_map) | NgramFilter(minsize=3)

title_field = TEXT(analyzer=analyzer, stored=True)
id_field = ID(unique=True, stored=True)

schema = Schema(
        id=id_field,
        title=title_field,
        story=STORED,
        )

ARCHIVE_LOCATION = 'data/archive'

ix = None

def init():
    global ix

    if exists_in(ARCHIVE_LOCATION):
        ix = open_dir(ARCHIVE_LOCATION)
    else:
        ix = create_in(ARCHIVE_LOCATION, schema)

def update(story):
    writer = ix.writer()
    writer.update_document(
            id=story['id'],
            title=story['title'],
            story=story,
            )
    writer.commit()

def get_story(sid):
    with ix.searcher() as searcher:
        result = searcher.document(id=sid)
        return result['story'] if result else None

def search(search):
    with ix.searcher() as searcher:
        query = QueryParser('title', ix.schema).parse(search)
        results = searcher.search(query)
        stories = [r['story'] for r in results]
        for s in stories:
            s.pop('text', '')
            s.pop('comments', '')
        return stories
