from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker
from .config import dbpath

engine = create_engine(dbpath)
Session = sessionmaker(bind=engine)

metadata = MetaData()
subs_table = Table('subscriptions', metadata,
    Column('name', String(64), primary_key=True, nullable=False)
)
subs_table.create(engine, checkfirst=True)
