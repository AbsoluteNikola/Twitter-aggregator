import requests
from json import loads
from secrets import SMMRY_key, SMMRY_length

def request_summary(text, is_url=False, sentences=SMMRY_length):
    parameters = {
        'SM_API_KEY': SMMRY_key,
        'SM_LENGTH': sentences,
        'SM_KEYWORD_COUNT': 3
    }
    if is_url:
        parameters['SM_URL'] = text
        resp = requests.post("https://api.smmry.com", params=parameters)
    else:
        post_data = {
            'sm_api_input': text
        }
        resp = requests.post("https://api.smmry.com", data=post_data, params=parameters)
    return loads(resp.text)
