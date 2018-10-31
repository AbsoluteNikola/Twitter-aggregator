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
    """Class representing users with necessary functionality

    Attributes
    ----------
    id : int
        User's id as used by twitter
    registered : DateTime
        Date and time at which this user first logged in
    preference : dict
        Dictionary of [keyword]->score pairs

    Methods
    -------
    score_twit(twit: Twit) -> float
        Score a twit based on preference
    update_pref(twit: Twit, score: float)
        Update preference for that particular twit.
        Score could be either positive or negative and will affect the preference accordingly

    OAuth
    ------
    Attributes representing an OAuth2 token:
    token_type
    access_token
    refresh_token
    expres_at

    token - dict of the above
    """
    __tablename__ = "users"
    __table_args__ = {'useexisting': True}

    user_id = Column('id', Integer, primary_key=True, nullable=False)
    registered = Column(DateTime, nullable=False)
    #oauth_token = Column(Unicode(128), nullable=False)
    #oauth_secret = Column(Unicode(128), nullable=False)
    #_liked_tweets_enc = Column("liked", Unicode(2018), nullable=False)
    # Just another jsoned value. There should be a better way to make these
    _preference_vector_enc = Column("preference", Unicode(2048), nullable=False)

    # token_type = Column(String(20))
    # access_token = Column(String(48), nullable=False)
    # refresh_token = Column(String(48))
    # expires_at = Column(Integer, default=0)

    def __init__(self, user_id, token=None, secret=None):
        self.user_id = user_id
        self.registered = datetime.now()
        self.preference = {}
        self.oauth_token = token
        self.oauth_secret = secret

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

    # @property
    # def token(self):
    #     return dict(
    #         access_token=self.access_token,
    #         token_type=self.token_type,
    #         refresh_token=self.refresh_token,
    #         expires_at=self.expires_at,
    #     )

    # @token.setter
    # def token_set(self, token):
    #     self.access_token = token['access_token']
    #     self.token_type = token['token_type']
    #     self.expires_at = token['expires_at']
    #     self.refresh_token = token['refresh_token']

    def __repr__(self):
        return f"<User id={self.user_id} registered_at={self.registered}>"

    def __str__(self):
        return f"<User {self.user_id}>"

Base.metadata.create_all(engine)
