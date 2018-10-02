import asyncio
import uvloop
from sqlalchemy.exc import IntegrityError
from .databaseManager import Session, engine, subs_table
from .twitterHandler import keep_twits_updated
from .Twit import Twit
from .config import update_timeout
from pprint import pprint
from logging import getLogger

logger = getLogger("aggregator.main")

def run():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    asyncio.ensure_future(keep_twits_updated())
    try:
        logger.info("Starting operation")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        loop.stop()
    loop.close()    

if __name__ == "__main__":
    print("This script cannot be run as is, please run the package itself.\n\tcd..\n\tpython aggregator")
