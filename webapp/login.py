from webapp import app
from authlib.flask.client import OAuth
from .config import c_key, c_secret
from flask import session, redirect, request, url_for
from aggregator import User

globtoken = None

def fetch_request_token():
    return globtoken
    return session.get('twitter_token')

def save_request_token(token=None):
    session['twitter_token'] = token
    globtoken = token

def fetch_twitter_token():
    curr_user = User.query.filter_by(User.id == session['current_user'].id).first()
    return curr_user.token()

oauth = OAuth(app)
twitter = oauth.register('twitter',
    client_id=c_key,
    client_secret=c_secret,
    api_base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    request_token_params=None,
    access_token_url='https://api.twitter.com/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    authorize_url='https://api.twitter.com/oauth/authenticate',
    client_kwargs=None,
    fetch_token=fetch_twitter_token,
    save_request_token=save_request_token,
    fetch_request_token=fetch_request_token,
)

@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return oauth.twitter.authorize_redirect(callback=redirect_uri)

@app.route('/authorized')
def authorized():
    token = oauth.twitter.authorize_access_token()
    session['twitter_token'] = token
    print(token)