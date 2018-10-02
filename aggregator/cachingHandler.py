import asyncio
from datetime import datetime, timedelta
from .config import cache_delay, max_age
from .User import User
from .Twit import Twit
from .databaseManager import Session, engine
from logging import getLogger

logger = getLogger("aggregator.cachingHandler")
session = None

async def update_cache(user:User):
    oldest_twit = datetime.now() - timedelta(minutes=max_age)
    new_twits = session.query(Twit).filter_by(Twit.created_at > oldest_twit).all()
    cache = []
    for twit in new_twits:
        usr_score = user.score_twit(twit)
        time_del = twit.created_at - oldest_twit
        time_score = max_age / time_del.total_seconds() * 100
        overall_score = usr_score * time_score
        cache.append((twit.id, overall_score))
    cache.sort(key=lambda tw: tw[1])
    #
    # Write dat cahce
    #

async def keep_cache_updated():
    global session
    loop = asyncio.get_event_loop()
    with Session as session:
        while True:
            users = session.query(User).all()
            for user in users:
                loop.ensure_future(update_cache(user))
            await asyncio.sleep(cache_delay)
