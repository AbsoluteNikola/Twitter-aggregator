import json
import twitter
from secrets import *
from pprint import pprint

# Credentials are stored in secrets.py
api = twitter.Api(consumer_key=c_key, consumer_secret=c_secret, access_token_key=at_key, access_token_secret=at_secret)

def strip_status(status:twitter.models.Status):
    stat_d = status.AsDict()
    return (
        stat_d['id'],
        stat_d['created_at'],
        stat_d['user']['screen_name'],
        stat_d['text']
    )

def get_timeline():
    global_timeline = []

    with open("following.txt", "r") as file:
        track = file.readlines()

    for name in track:
        global_timeline.extend(api.GetUserTimeline(screen_name=name))

    global_timeline.sort(key=lambda x: x.created_at_in_seconds)
    # status.created_at_in_seconds - returns utc timestamp
    global_timeline = [strip_status(status) for status in global_timeline]
    return global_timeline

if __name__ == '__main__':
    pprint(get_timeline())
