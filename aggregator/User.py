import json
from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import DateTime, Unicode
from sqlalchemy.orm import column_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from .databaseManager import Session, engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'useexisting': True}

    id = Column(Integer, primary_key=True)
    registered = Column(DateTime, nullable=False)
    #_liked_tweets_enc = Column("liked", Unicode(2018), nullable=False)
    # Just another jsoned value. There should be a better way to make these
    _preference_vector_enc = Column("preference", Unicode(2048), nullable=False)

    def __init__(self):
        self.registered = datetime.now()
        self.preference = {}

    @property
    def preference(self) -> list:
        return json.loads(self._preference_vector_enc)
    
    @preference.setter
    def preference(self, new_pref: list):
        self._preference_vector_enc = json.dumps(new_pref, separators=(',', ':'))

    def score_twit(self, twit):
        score = 0
        for key, val in twit.keywords:
            try:
                score += self.preference[key] * val
            except KeyError:
                pass
        return score
    
    def update_pref(self, twit, score):
        for key, val in twit.keywords:
            curr_pref = 1
            try:
                curr_pref = self.preference[key]
            except KeyError:
                pass
            self.preference[key] = curr_pref + val * score # Positive or negative

    def __repr__(self):
        return f"<User id={self.id} registered_at={self.registered}>"

    def __str__(self):
        return f"<User {self.id}>"

Base.metadata.create_all(engine)
