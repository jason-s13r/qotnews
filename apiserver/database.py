import json

from sqlalchemy import create_engine, Column, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///data/qotnews.sqlite')
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Story(Base):
    __tablename__ = 'stories'

    sid = Column(String(16), primary_key=True)
    meta_json = Column(String)
    full_json = Column(String)

class Reflist(Base):
    __tablename__ = 'reflist'

    rid = Column(Integer, primary_key=True)
    ref = Column(String(16), unique=True)
    sid = Column(String, ForeignKey('stories.sid'), unique=True)

def init():
    Base.metadata.create_all(engine)

def get_meta(sid):
    session = Session()
    return session.query(Story).get(sid).meta_json

def get_full(sid):
    session = Session()
    return session.query(Story).get(sid).full_json

def put_story(story):
    full_json = json.dumps(story)

    story.pop('text')
    story.pop('comments')
    meta_json = json.dumps(story)

    try:
        session = Session()
        s = Story(sid=story['id'], full_json=full_json, meta_json=meta_json)
        session.merge(s)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close() 

def get_reflist(amount):
    session = Session()
    q = session.query(Reflist).order_by(Reflist.rid.desc()).limit(amount)
    return [dict(ref=x.ref, sid=x.sid) for x in q.all()]

def put_ref(ref, sid):
    try:
        session = Session()
        r = Reflist(ref=ref, sid=sid)
        session.add(r)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    init()
