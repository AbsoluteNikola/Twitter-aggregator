from os import urandom
from pprint import pprint
from time import time
from base64 import b64encode
from urllib.parse import quote_plus as quote
from hashlib import sha1, md5
from itertools import chain
import requests as rq
import hmac

callback = 'http://94.140.251.57:9876/twitter'
qcallbc = quote(callback)
twitter = 'https://api.twitter.com/oauth/request_token'
c_key = 
c_secret = ''
s = rq.Session()


def sign_request(method: str, url: str, parameters: dict, **kwargs) -> str:
    sign_keys = []
    for key, val in chain(parameters.items(), kwargs.items()):
        sign_keys.append(
            (quote(key), quote(val))
        )
    sign_keys.sort(key=lambda x: x[0])
    print("keys", sign_keys)
    sign_str = '&'.join(['='.join(pair) for pair in sign_keys])
    print("str", sign_str)
    sign_parts = [method, url, sign_str]
    sign = '&'.join(map(quote, sign_parts))
    print("sign", sign)
    return sign


def request_token():
    t = str(int(time()))
    # t = 1300228849
    nonce = md5(urandom(24)).hexdigest()
    # oldsign = f'POST&{twitter}&oauth_callback=%3D{qcallbc}%%26oauth_consumer_key%3D{c_key}%26oauth_nonce%3D{nonce}%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D{t}%26oauth_version%3D1.0'
    # oldsign = hmac_sha1(oldsign)
    credentials = {
        'oauth_callback': callback,
        'oauth_consumer_key': c_key,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': t,
        'oauth_version': '1.0'
    }
    sign = sign_request('POST', twitter, {}, **credentials)
    sign = hmac_sha1(sign, c_secret)
    pprint(sign)
    credentials['oauth_callback'] = qcallbc
    header_parts = chain(credentials.items(), (("oauth_signature", sign),))
    header_parts = list(header_parts)
    header_parts.sort(key=lambda x: x[0])
    header = 'OAuth ' + ', '.join([f'{key}="{val}"' for key, val in header_parts])
    print(header)
    headers = {
        'Authorization': header,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    pprint(headers['Authorization'])
    x = s.post('https://api.twitter.com/oauth/request_token', headers=headers)
    pprint(x)
    pprint(x.text)


def hmac_sha1(msg, consumer_key='', access_token=''):
    hashed = hmac.new(f'{consumer_key}&{access_token}'.encode('ascii'), msg.encode('ascii'), sha1)
    return quote(b64encode(hashed.digest()).decode('ascii'))


request_token()
