from webapp import app
from .config import c_key, c_secret
from flask import session, redirect, request, url_for, render_template, redirect, make_response
from aggregator import User
from json import dumps, loads, JSONDecodeError
from urllib.parse import quote_plus as quote
import requests as rq
from time import time
from hashlib import md5, sha1
from os import urandom
from base64 import b64encode
from itertools import chain
from pprint import pprint
from twitter.api import Api
import hmac

globtoken = None
twitter_rq_token = 'https://api.twitter.com/oauth/request_token'
twitter_auth_red = 'https://api.twitter.com/oauth/authenticate'
twitter_ac_token = 'https://api.twitter.com/oauth/access_token'
twitter_verify_c = 'https://api.twitter.com/1.1/account/verify_credentials.json'

def sign_request(method: str, url: str, parameters: dict, **kwargs) -> str:
    sign_keys = []
    for key, val in chain(parameters.items(), kwargs.items()):
        sign_keys.append(
            (quote(key), quote(val))
        )
    sign_keys.sort(key=lambda x: x[0])
    sign_str = '&'.join(['='.join(pair) for pair in sign_keys])
    sign_parts = [method, url, sign_str]
    sign = '&'.join(map(quote, sign_parts))
    return sign

def hmac_sha1(msg, consumer_key='', access_token=''):
    hashed = hmac.new(f'{consumer_key}&{access_token}'.encode('ascii'), msg.encode('ascii'), sha1)
    return quote(b64encode(hashed.digest()).decode('ascii'))

def make_api_request(method, url, params=None, payload=None, creds=None, access_token=None, *args, **kwargs):
    # Add new data
    sign = sign_request('POST', twitter_rq_token, params, **creds, **payload)
    sign = hmac_sha1(sign, c_secret, access_token or '')
    if 'add_sign_to_params' in kwargs and kwargs['add_sign_to_params'] == True:
        params['oauth_signature'] = sign
    if 'oauth_callback' in creds.keys():
        creds['oauth_callback'] = quote(creds['oauth_callback'])
    # sort parameters
    params = {key:val for key, val in sorted(params.items())}
    # sort headers
    header_parts = list(creds.items())
    header_parts.append(("oauth_signature", sign))
    header_parts.sort(key=lambda x: x[0])
    header = 'OAuth ' + ', '.join([f'{key}="{val}"' for key, val in header_parts])
    headers = {
        'Authorization': header,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    # sort payload
    payload_parts = list(payload.items())
    payload_parts.sort(key=lambda x: x[0])
    bin_data = b'&'.join([(f'{key}={val}').encode() for key, val in payload_parts])
    # Make request
    resp = rq.__getattribute__(method.lower())(url, params=params, headers=headers, data=bin_data)
    #pprint(resp)
    #if not resp.ok:
    #    raise ValueError(resp.text)
    txt = resp.text
    pprint(txt)
    return txt

def make_oauth_credentials(**kwargs):
    t = str(int(time()))
    nonce = md5(urandom(24)).hexdigest()
    credentials = {
        'oauth_consumer_key': c_key,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': t,
        'oauth_version': '1.0',
        **kwargs
    }
    return credentials

def get_request_token():
    credentials = make_oauth_credentials(oauth_callback=url_for('authorized', _external=True))
        
    resp = make_api_request('POST', twitter_rq_token, {}, {}, credentials)
    ret = {pair.split('=')[0]:pair.split('=')[1] for pair in resp.split('&')}
    return ret

def get_access_token(request_token, verifier):
    credentials = make_oauth_credentials(oauth_token=request_token)
    payload = {
        'oauth_verifier': verifier
    }
    resp = make_api_request('POST', twitter_ac_token, {}, credentials, payload)
    ret = {pair.split('=')[0]:pair.split('=')[1] for pair in resp.split('&')}
    return ret

def verify_credentials():
    oauth_token = session['oauth_access_token']
    credentials = make_oauth_credentials(oauth_token=oauth_token)
    params = credentials
    resp = make_api_request('GET', twitter_verify_c, params, credentials, {}, add_sign_to_params=True)
    try:
        ret = loads(resp)
    except JSONDecodeError:
        ret = resp
    return ret

@app.route('/login')
def login():
    token = get_request_token()
    if token['oauth_callback_confirmed'] != 'true':
        return render_template('404.html'), 401 # !!!!!
    session['oauth_token'] = token['oauth_token']
    session['oauth_token_secret'] = token['oauth_token_secret']
    return redirect(twitter_auth_red + "?oauth_token={}".format(session['oauth_token']), code=302)

@app.route('/authorized')
def authorized():
    token = request.args.get('oauth_token')
    verifier = request.args.get('oauth_verifier')
    if token != session['oauth_token']:
        return render_template("404.html"), 401 #!!!
    access_token = get_access_token(token, verifier)
    session['oauth_access_token'] = access_token['oauth_token']
    session['oauth_access_token_secret'] = access_token['oauth_token_secret']
    session['twitter_user_id'] = access_token['user_id']
    session['twitter_screen_name'] = access_token['screen_name']
    pprint(verify_credentials())
    # a = Api(
    #     consumer_key=c_key,
    #     consumer_secret=c_secret,
    #     access_token_key=session['oauth_access_token'],
    #     access_token_secret=session['oauth_access_token_secret']
    # )
    #pprint(a.VerifyCredentials())
    session['logged_in'] = True
    redirect_url = session.pop('next', url_for('index'))
    return redirect(redirect_url)

@app.route('/logout')
def logout():
    session.pop('oauth_token')
    session.pop('oauth_token_secret')
    session.pop('oauth_access_token')
    session.pop('oauth_access_token_secret')
    session.pop('logged_in')

    redirect_url = session.pop('next', url_for('index'))

    return redirect(redirect_url)
