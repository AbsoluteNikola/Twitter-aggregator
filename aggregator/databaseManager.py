import sqlalchemy
from secrets import dbpath
from sqlalchemy.orm import sessionmaker

engine = sqlalchemy.create_engine(dbpath)
Session = sessionmaker(bind=engine)
