from datetime import datetime, timedelta
from json import dumps, loads, JSONDecodeError
from urllib.parse import quote_plus as quote
from functools import wraps
import requests as rq
from pprint import pprint
from aggregator import User, Twit
from flask import session, redirect, request, url_for, render_template, redirect, make_response, g, jsonify
from werkzeug.local import LocalProxy
from webapp import app
from .config import c_key, c_secret
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker
from .config import dbpath, cachedir

logger = app.logger
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
            # print("Current user: %s (id %d)" % (session['twitter_screen_name'], session['twitter_user_id']))
            if 'user' not in g:
                user = db.query(User).filter(User.user_id == session['twitter_user_id']).one_or_none()
                if not user:
                    user = User(session['twitter_user_id'],
                                session['oauth_access_token'],
                                session['oauth_access_token_secret'])
                    # print("New user", user)
                    logger.debug("New user %s" % user.user_id)
                    db.add(user)
                g.user = user
            logger.debug("Current user %s" % g.user)
            return g.user        
        else:
            return None
    except KeyError:
        return None

@app.teardown_appcontext
def teardown_user(ctx):
    user = g.pop('user', None)

db = LocalProxy(get_db)
user:User = LocalProxy(get_user)

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

def xhr_handler(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if request.is_xhr or request.is_json:
            data = request.json or request.form
        else:
            data = request.form
        data = dict(data)
        logger.info("AJAX data %s" % data)
        ret = func(data, *args, **kwargs)
        return ret
    return deco

@app.route('/feed')
def feed():
    feed = get_feed()
    return render_template('feed.html.j2', feed=feed)

@app.route('/feed/action', methods=['POST'])
@xhr_handler
def action(data):
    try:
        action = data['action'][0]
        twit_id = data['id'][0]
    except KeyError:
        action = None
    twit = db.query(Twit).filter(Twit.id == twit_id).one_or_none()
    if action == 'like':
        user.update_pref(twit, 1.0)
        return jsonify({'status': 'success'})
    elif action == 'dislike':
        user.update_pref(twit, -1.0)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'error': {'code': 422, 'message': "Wrong action"}}), 422
