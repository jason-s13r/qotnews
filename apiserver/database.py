from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import JSON, DateTime, String, Integer
from utils import gen_rand_id
import json

engine = create_engine('sqlite:///data/qotnews_proto.sqlite', connect_args={'timeout': 120})
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
            if isinstance(obj, datetime):
                return obj.isoformat()

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
    ref = Column(String)
    source = Column(String)
    sourceref = Column(String, unique=True)
    data = Column(JSON)
    last_updated = Column(DateTime)

    content = relationship("Content", back_populates="sources")

class Queue(Base):
    __tablename__ = 'queue'
    ref = Column(String, primary_key=True)
    source = Column(String, primary_key=True)
    url = Column(String)
    sid = Column(String, ForeignKey('source.sid'), unique=True)
    last_updated = Column(DateTime)
    retries = Column(Integer, default=0)
    next_try = Column(DateTime)

def init():
    Base.metadata.create_all(engine)

def put_queue(ref, source, url=None):
    try:
        session = Session()
        s = Queue(ref=ref, source=source, url=url, last_updated=datetime.now(), next_try=datetime.now())
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

def update_queue(queue):
    try:
        session = Session()
        queue.last_updated = datetime.now()
        queue.retries += 1
        queue.next_try = datetime.now() + timedelta(minutes=15)
        session.merge(queue)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def get_queue(ref=None, source=None):
    session = Session()
    if not ref or not source:
        return session.\
            query(Queue).\
            filter(Queue.retries < 5).\
            filter(Queue.next_try < datetime.now()).\
            order_by(Queue.retries.asc(), Queue.last_updated.desc()).\
            all()
    return session.query(Queue).get((ref, source))

def put_source(source):
    source = dict(source)
    src = source.get('source')
    ref = source.get('ref')
    source.pop('content', None)
    source['sourceref'] = f"{src}:{ref}"
    source['last_updated'] = datetime.now()
    try:
        session = Session()
        if not source.get('sid', None):
            existing = get_source_by_ref(src, ref)
            if existing:
                source['sid'] = existing.sid
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

def get_source_by_ref(ref, source=None):
    session = Session()
    q = session.query(Source).filter(Source.ref == ref)
    if source is None: return q.all()
    return q.filter(Source.source == source).first()

def get_source_by_url(url, source=None):
    session = Session()
    q = session.query(Source).filter(Source.url == url)
    if source is None: return q.all()
    return q.filter(Source.source == source).first()

def get_source_for_scraping():
    session = Session()
    return session.query(Source).\
        join(Content, Content.url == Source.url, isouter=True).\
        filter(Content.cid == None).\
        filter(Source.sid != None).\
        order_by(Source.data['date'].desc()).\
        all()

def put_content(content):
    content = dict(content)
    content.pop('source', None)
    content['last_updated'] = datetime.now()
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
        filter(Content.url != None).\
        order_by(Content.last_updated.asc()).\
        all()

def get_feed(maxage=0, skip=0, limit=20):
    time = datetime.now().timestamp() - maxage
    session = Session()
    q = session.query(Source).\
            join(Content).\
            filter(Source.source != 'manual').\
            filter(maxage == 0 or Source.data['date'].as_integer() > time).\
            order_by(Source.data['date'].desc()).\
            offset(skip).\
            limit(limit)
    return q.all()
