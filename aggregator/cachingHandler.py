from time import sleep
from datetime import datetime, timedelta
from .config import cache_delay, max_age, cachedir
from .User import User
from .Twit import Twit
from .databaseManager import Session, engine
from logging import getLogger

logger = getLogger("aggregator.cachingHandler")
session = Session()

def export_cache(user:User, cache):
    file = cachedir / str(user.user_id)
    with open(file, "w") as f:
        for twit in cache:
            f.write("%d:%d\n" % twit)

def update_cache(user:User):
    logger.info("Updating cache for user %s" % str(user))
    oldest_twit = datetime.now() - timedelta(minutes=max_age)
    new_twits = session.query(Twit).filter(Twit.created_at > oldest_twit).all()
    logger.log(5, "Available twits %s" % new_twits)
    cache = []
    for twit in new_twits:
        usr_score = user.score_twit(twit)
        time_del = twit.created_at - oldest_twit
        time_score = max_age / time_del.total_seconds() * 100
        overall_score = usr_score * time_score
        cache.append((twit.id, overall_score))
    cache.sort(key=lambda tw: tw[1])
    logger.debug("New cache: %s" % str(cache))
    export_cache(user, cache)

def keep_cache_updated():
    logger.info("Caching started")
    while True:
        logger.info("New caching run")
        users = session.query(User).all()
        logger.debug("User list: %s" % str(users))
        for user in users:
            update_cache(user)
        logger.info("Sleeping for %d seconds" % cache_delay)
        sleep(cache_delay)
