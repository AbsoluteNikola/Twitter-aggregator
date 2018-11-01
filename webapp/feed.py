from datetime import datetime, timedelta
from json import dumps, loads, JSONDecodeError
from urllib.parse import quote_plus as quote
import requests as rq
from pprint import pprint
from aggregator import User, Twit
from flask import session, redirect, request, url_for, render_template, redirect, make_response, g
from werkzeug.local import LocalProxy
from webapp import app
from .config import c_key, c_secret
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker
from .config import dbpath, cachedir

engine = create_engine(dbpath)
Sessionmk = sessionmaker(bind=engine)

def get_db():
    if 'db' not in g:
        db_session = Sessionmk()
        g.db = db_session
    return g.db

@app.teardown_appcontext
def teardown_db(ctx):
    db = g.pop('db', None)
    if db is not None:
        db.commit()
        db.close()

def get_user():
    try:
        if session['logged_in'] == True:
            print("Current user: %s (id %d)" % (session['twitter_screen_name'], session['twitter_user_id']))
            if 'user' not in g:
                user = db.query(User).filter(User.user_id == session['twitter_user_id']).one_or_none()
                if not user:
                    user = User(session['twitter_user_id'],
                                session['oauth_access_token'],
                                session['oauth_access_token_secret'])
                    print("New user", user)
                    db.add(user)
                g.user = user
            pprint(g.user)
            return g.user        
        else:
            return None
    except KeyError:
        return None

@app.teardown_appcontext
def teardown_user(ctx):
    user = g.pop('user', None)

db = LocalProxy(get_db)
user = LocalProxy(get_user)

def read_user_cache(user:User):
    if user is None: raise ValueError
    file = cachedir / str(user.user_id)
    cache = []
    if file.exists():
        with open(file, "r") as f:
            cache = [ tuple(map(int, twit.split(":"))) for twit in f.readlines() ]
    return cache

def get_feed():
    twits = []
    if user:
        twits = read_user_cache(user)
        twits.sort(key=lambda x: x[1])
        twits = [
            db.query(Twit).filter(Twit.id == twit[0]).one_or_none()
            for twit in twits
        ]
    else:
        oldest_twit = datetime.now() - timedelta(hours=24)
        twits = db.query(Twit).filter(Twit.created_at > oldest_twit).all()
    return twits

@app.route('/feed')
def feed():
    feed = get_feed()
    return render_template('feed.html.j2', feed=feed)
