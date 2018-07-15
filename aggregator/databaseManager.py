import sqlalchemy
from sqlalchemy.orm import sessionmaker
from .secrets import dbpath

engine = sqlalchemy.create_engine(dbpath)
Session = sessionmaker(bind=engine)
