import json

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///data/qotnews.sqlite')
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Story(Base):
    __tablename__ = 'stories'

    sid = Column(String, primary_key=True)
    meta_json = Column(String)
    full_json = Column(String)

def init():
    Base.metadata.create_all(engine)

def get_meta(sid):
    session = Session()
    return session.query(Story).get(sid).meta_json

def get_full(sid):
    session = Session()
    return session.query(Story).get(sid).full_json

def put(story):
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
