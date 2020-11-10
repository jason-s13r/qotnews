from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import JSON

engine = create_engine('sqlite:///data/qotnews.sqlite')
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Story(Base):
    __tablename__ = 'stories'

    sid = Column(String(16), primary_key=True)
    ref = Column(String(16), unique=True)
    meta = Column(JSON)
    data = Column(JSON)
    title = Column(String)

class Reflist(Base):
    __tablename__ = 'reflist'

    rid = Column(Integer, primary_key=True)
    ref = Column(String(16), unique=True)
    sid = Column(String, ForeignKey('stories.sid'), unique=True)
    source = Column(String(16))

def init():
    Base.metadata.create_all(engine)

def get_story(sid):
    session = Session()
    return session.query(Story).get(sid)

def put_story(story):
    story = story.copy()
    data = {}
    data.update(story)

    meta = {}
    meta.update(story)
    meta.pop('text', None)
    meta.pop('comments', None)

    try:
        session = Session()
        s = Story(
            sid=story['id'],
            ref=story['ref'],
            data=data,
            meta=meta,
            title=story.get('title', None),
        )
        session.merge(s)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close() 

def get_story_by_ref(ref):
    session = Session()
    return session.query(Story).filter(Story.ref==ref).first()

def get_stories_by_url(url):
    session = Session()
    return session.query(Story).\
            filter(Story.title != None).\
            filter(Story.meta['url'].as_string() == url).\
            order_by(Story.meta['date'].desc())

def get_reflist():
    session = Session()
    q = session.query(Reflist).order_by(Reflist.rid.desc())
    return [dict(ref=x.ref, sid=x.sid, source=x.source) for x in q.all()]

def get_stories(maxage=60*60*24*2):
    time = datetime.now().timestamp() - maxage
    session = Session()
    q = session.query(Reflist, Story.meta).\
            join(Story).\
            filter(Story.title != None).\
            filter(Story.meta['date'] > time).\
            order_by(Story.meta['date'].desc())
    return [x[1] for x in q]

def put_ref(ref, sid, source):
    try:
        session = Session()
        r = Reflist(ref=ref, sid=sid, source=source)
        session.add(r)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def del_ref(ref):
    try:
        session = Session()
        session.query(Reflist).filter(Reflist.ref==ref).delete()
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    init()

    print(get_story_by_ref('hgi3sy'))
