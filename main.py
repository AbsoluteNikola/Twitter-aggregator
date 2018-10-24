import asyncio
import uvloop
import argparse
from aggregator import keep_twits_updated, keep_cache_updated
from webapp import app
from pprint import pprint
from logging import getLogger

logger = getLogger("aggregator.main")


def setup_parser():
    arg_parser = argparse.ArgumentParser(description="Hub for using the backend of the twitter aggregator")
    arg_parser.add_argument('--verbose', '-v', action='count', help="Set verbosity level from 0 to 3")
    subparser = arg_parser.add_subparsers(help='Available commands', dest='command')

    parse_twitter = subparser.add_parser("twit", help="Run twitter and caching backends")
    parse_webapp = subparser.add_parser("web", help="Run Flask webserver")

    return arg_parser


def run():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    asyncio.ensure_future(keep_twits_updated())
    asyncio.ensure_future(keep_cache_updated())
    try:
        logger.info("Starting operation")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        loop.stop()
    loop.close()


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    if args.command == "twit":
        run()
    elif args.command == "web":
        app.run(host="0.0.0.0", debug=True)
    else:
        parser.print_usage()
