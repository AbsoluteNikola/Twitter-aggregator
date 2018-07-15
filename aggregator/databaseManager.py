import sqlalchemy
from sqlalchemy.orm import sessionmaker
from .config import dbpath

engine = sqlalchemy.create_engine(dbpath)
Session = sessionmaker(bind=engine)
