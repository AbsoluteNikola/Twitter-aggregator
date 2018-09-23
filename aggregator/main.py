import asyncio
import uvloop
from sqlalchemy.exc import IntegrityError
from .databaseManager import Session, engine, subs_table
from .twitterHandler import get_timeline
from .Twit import Twit
from .config import update_timeout
from pprint import pprint
from logging import getLogger

logger = getLogger("aggregator.main")
session = Session()

async def update_db(users):
    timeline = get_timeline(users)
    for twit in timeline:
        old_tw = session.query(Twit).filter(Twit.id == twit.id).one_or_none()
        if not old_tw:
            logger.debug("New twit")
            session.add(twit)
        else:
            logger.debug("Duplicate twit")
    session.commit()

async def keep_updated(users):
    while True:
        logger.info("New update")
        await update_db(users)
        logger.info("Waiting %d seconds" % update_timeout)
        await asyncio.sleep(update_timeout)

def run():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    subs = [res[0] for res in engine.execute(subs_table.select()).fetchall()]
    logger.debug("Tracking %s" % str(subs))

    asyncio.ensure_future(keep_updated(subs))
    try:
        logger.info("Starting operation")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        loop.stop()
    loop.close()
    session.close()
    

if __name__ == "__main__":
    print("This script cannot be run as is, please run the package itself.")
