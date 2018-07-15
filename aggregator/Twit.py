import json
from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import DateTime, Unicode
from sqlalchemy.orm import column_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from categorizer import get_keywords
from databaseManager import Session, engine

Base = declarative_base()

class Twit(Base):
    __tablename__ = "twits"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    user = Column(Unicode(64))
    text = Column(Unicode(150))
    keywords_arr = []

    @hybrid_property
    def keywords(self):
        return json.dumps(self.keywords_arr)

    def __init__(self, info: tuple):
        self.id = info[0]
        self.created_at = datetime.strptime(info[1], "%a %b %d %H:%M:%S %z %Y")
        self.user = info[2]
        self.text = info[3]
        self.keywords_arr = get_keywords(self.text)

Base.metadata.create_all(engine)