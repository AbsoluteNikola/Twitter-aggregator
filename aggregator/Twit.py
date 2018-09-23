import json
from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import DateTime, Unicode
from sqlalchemy.orm import column_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from .categorizer import get_keywords
from .databaseManager import Session, engine

Base = declarative_base()

class Twit(Base):
    __tablename__ = "twits"
    __table_args__ = {'useexisting': True}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    user = Column(Unicode(64))
    text = Column(Unicode(150))
    _keywords_str = Column('keywords', Unicode(500))

    @property
    def keywords(self) -> list:
        return json.loads(self._keywords_str)
    
    @keywords.setter
    def keywords(self, new_keywords: list):
        self._keywords_str = json.dumps(new_keywords, separators=(',', ':'))

    def __init__(self, info: tuple):
        self.id = info[0]
        self.created_at = datetime.strptime(info[1], "%a %b %d %H:%M:%S %z %Y") # Date format is "Tue May 1 16:45:37 +0000 2018"
        self.user = info[2]
        self.text = info[3]
        self.keywords = get_keywords(self.text)

    def __repr__(self):
        return f"<Twit id={self.id} user='{self.user}' created_at={self.created_at} text='{self.text}'>"

    def __str__(self):
        return f"'{self.text}'\n\tby {self.user} at {self.created_at}"

    def __hash__(self): # Enables abject hashing. Used in dictionaries.
        return self.id

Base.metadata.create_all(engine)