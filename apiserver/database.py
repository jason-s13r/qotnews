from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import JSON, DateTime, String, Integer
from utils import gen_rand_id
import json

engine = create_engine('sqlite:///data/qotnews.sqlite', connect_args={'timeout': 120})
Session = sessionmaker(bind=engine)

Base = declarative_base()


def new_alchemy_encoder():
    _visited_objs = []
    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    fields[field] = obj.__getattribute__(field)
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder

def new_content_id():
    nid = gen_rand_id()
    while get_content(nid):
        nid = gen_rand_id()
    return nid

def new_source_id():
    nid = gen_rand_id()
    while get_source(nid):
        nid = gen_rand_id()
    return nid

def as_dict(o):
    return {c.name: getattr(o, c.name) for c in o.__table__.columns}

# loosely matching a readable (output of declutter/outline/readability.js)
class Content(Base):
    __tablename__ = 'content'
    cid = Column(String, primary_key=True, unique=True, default=new_content_id)
    url = Column(String, unique=True, index=True)
    scraper = Column(String)
    details = Column(JSON)
    last_updated = Column(DateTime)

    sources = relationship("Source", back_populates="content")

# sources, also where comments are stored.
class Source(Base):
    __tablename__ = 'source'
    sid = Column(String, primary_key=True, unique=True, default=new_source_id)
    url = Column(String, ForeignKey('content.url'))
    source = Column(String)
    data = Column(JSON)
    last_updated = Column(DateTime)

    content = relationship("Content", back_populates="sources")

class Queue(Base):
    __tablename__ = 'item'
    ref = Column(String, primary_key=True)
    source = Column(String, primary_key=True)
    url = Column(String)
    sid = Column(String, ForeignKey('source.sid'), unique=True)

####

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
    urlref = Column(String)
    sid = Column(String, ForeignKey('stories.sid'), unique=True)
    source = Column(String(16))

def init():
    Base.metadata.create_all(engine)

def put_queue(ref, source, url=None):
    try:
        session = Session()
        s = Queue(ref=ref, source=source, url=url)
        session.merge(s)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def del_queue(ref, source):
    try:
        session = Session()
        session.query(Queue).filter(Queue.ref==ref).filter(Queue.source==source).delete()
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def get_queue(ref=None, source=None):
    session = Session()
    q = session.query(Queue)
    if not ref or not source: return q.all()
    return q.get((ref, source))

def put_source(source):
    source = dict(source)
    try:
        session = Session()
        s = Source(**source)
        session.merge(s)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def get_source(sid=None):
    session = Session()
    q = session.query(Source)
    if not sid: return q.all()
    return q.get(sid)

def put_content(content):
    content = dict(content)
    try:
        session = Session()
        if not content.get('cid', None):
            existing = get_content_by_url(content.get('url', ''))
            if existing:
                content['cid'] = existing.cid
        s = Content(**content)
        session.merge(s)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def get_content(cid=None):
    session = Session()
    q = session.query(Content)
    if not cid: return q.all()
    return q.get(cid)

def get_content_by_url(url):
    session = Session()
    return session.query(Content).\
        filter(Content.url == url).\
        first()

def get_content_for_scraping():
    session = Session()
    return session.query(Content).\
        filter(Content.details == None).\
        all()
###

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

def get_story_by_url(url):
    session = Session()
    return session.query(Story).\
            filter(Story.title != None).\
            filter(Story.meta['url'].as_string() == url).\
            order_by(Story.meta['date'].desc()).\
            first()

def get_stories_by_url(url):
    session = Session()
    return session.query(Story).\
            filter(Story.title != None).\
            filter(Story.meta['url'].as_string() == url).\
            order_by(Story.meta['date'].desc())

def get_ref_by_sid(sid):
    session = Session()
    x = session.query(Reflist).\
        filter(Reflist.sid == sid).\
        first()
    return dict(ref=x.ref, sid=x.sid, source=x.source, urlref=x.urlref)

def get_reflist():
    session = Session()
    q = session.query(Reflist).order_by(Reflist.rid.desc())
    return [dict(ref=x.ref, sid=x.sid, source=x.source, urlref=x.urlref) for x in q.all()]

def get_stories(maxage=0, skip=0, limit=20):
    time = datetime.now().timestamp() - maxage
    session = Session()
    q = session.query(Reflist, Story.meta).\
            join(Story).\
            filter(Story.title != None).\
            filter(maxage == 0 or Story.meta['date'].as_integer() > time).\
            order_by(Story.meta['date'].desc()).\
            offset(skip).\
            limit(limit)
    return [x[1] for x in q]

def put_ref(ref, sid, source, urlref):
    try:
        session = Session()
        r = Reflist(ref=ref, sid=sid, source=source, urlref=urlref)
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
