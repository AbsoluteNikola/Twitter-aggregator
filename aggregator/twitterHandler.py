import json
import twitter
from pprint import pprint
from .Twit import Twit
from .config import c_key, c_secret, at_key, at_secret
from logging import getLogger

logger = getLogger("aggregator.twitterHandler")
# Credentials are stored in the config file
api = twitter.Api(consumer_key=c_key, consumer_secret=c_secret, access_token_key=at_key, access_token_secret=at_secret)

def strip_status(status: twitter.models.Status):
    stat_d = status.AsDict()
    return (
        stat_d['id'],
        stat_d['created_at'],
        stat_d['user']['screen_name'],
        stat_d['text']
    )

def get_timeline(users):
    global_timeline = []

    for name in users:
        try:
            new_timeline = api.GetUserTimeline(screen_name=name)
            global_timeline.extend(new_timeline)
        except twitter.error.TwitterError as e:
            if e[0]['code'] == 34:
                logger.exception("No such user!!!")

    global_timeline.sort(key=lambda x: x.created_at_in_seconds)
    # status.created_at_in_seconds - returns utc timestamp
    global_timeline = [Twit(strip_status(status)) for status in global_timeline]
    return global_timeline

if __name__ == '__main__':
    pprint(get_timeline(""))
