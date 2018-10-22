from webapp import app
from .config import c_key, c_secret
from flask import session, redirect, request, url_for, render_template, redirect, make_response
from aggregator import User
from urllib.parse import quote_plus as quote
import requests as rq
from time import time
from hashlib import md5, sha1
from os import urandom
from base64 import b64encode
from itertools import chain
from pprint import pprint
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

def get_request_token():
    t = str(int(time()))
    nonce = md5(urandom(24)).hexdigest()
    credentials = {
        'oauth_callback': url_for('authorized', _external=True),
        'oauth_consumer_key': c_key,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': t,
        'oauth_version': '1.0'
    }
    sign = sign_request('POST', twitter_rq_token, {}, **credentials)
    sign = hmac_sha1(sign, c_secret)
    credentials['oauth_callback'] = quote(credentials['oauth_callback'])
    header_parts = list(credentials.items())
    header_parts.append(("oauth_signature", sign))
    header_parts.sort(key=lambda x: x[0])
    header = 'OAuth ' + ', '.join([f'{key}="{val}"' for key, val in header_parts])
    headers = {
        'Authorization': header,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    resp = rq.post(twitter_rq_token, headers=headers)
    params = resp.text
    pprint(params)
    ret = {pair.split('=')[0]:pair.split('=')[1] for pair in params.split('&')}
    return ret

def get_access_token(request_token, verifier):
    t = str(int(time()))
    nonce = md5(urandom(24)).hexdigest()
    credentials = {
        'oauth_token': request_token,
        'oauth_consumer_key': c_key,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': t,
        'oauth_version': '1.0'
    }
    parameters = {
        'oauth_verifier': verifier
    }
    sign = sign_request('POST', twitter_ac_token, parameters, **credentials)
    sign = hmac_sha1(sign, c_secret)
    header_parts = list(credentials.items())
    header_parts.append(("oauth_signature", sign))
    header_parts.sort(key=lambda x: x[0])
    header = 'OAuth ' + ', '.join([f'{key}="{val}"' for key, val in header_parts])
    headers = {
        'Authorization': header,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    bin_data = b'&'.join([(f'{key}={val}').encode() for key, val in parameters.items()])
    resp = rq.post(twitter_ac_token, headers=headers, data=bin_data)
    params = resp.text
    pprint(params)
    ret = {pair.split('=')[0]:pair.split('=')[1] for pair in params.split('&')}
    return ret

def verify_credentials():
    t = str(int(time()))
    nonce = md5(urandom(24)).hexdigest()
    oauth_token = session['oauth_access_token']
    credentials = {
        'oauth_consumer_key': c_key,
        'oauth_token': oauth_token,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': t,
        'oauth_version': '1.0'
    }
    sign = sign_request('GET', twitter_verify_c, credentials)
    sign = hmac_sha1(sign, c_secret, oauth_token)
    resp = rq.get(twitter_verify_c, params=credentials)
    ans = resp.json()
    pprint(ans)
    return ans

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
    session['logged_in'] = True
    verify_credentials()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('oauth_token')
    session.pop('oauth_token_secret')
    session.pop('oauth_access_token')
    session.pop('oauth_access_token_secret')
    session.pop('logged_in')

    return redirect(url_for('index'))
