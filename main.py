#!/bin/python3
import sys
import asyncio
import uvloop
import argparse
from aggregator import keep_twits_updated, keep_cache_updated, add_subscription
from webapp import app
from pprint import pprint
from logging import getLogger

logger = getLogger("aggregator.main")


def setup_parser():
    arg_parser = argparse.ArgumentParser(description="Hub for using the backend of the twitter aggregator")
    arg_parser.add_argument('--verbose', '-v', action='count', help="Set verbosity level from 0 to 3")
    subparser = arg_parser.add_subparsers(help='Available commands', dest='command')

    # parse_twitter = subparser.add_parser("twit", help="Run twitter and caching backends")
    # parse_webapp = subparser.add_parser("web", help="Run Flask webserver")
    parse_run = subparser.add_parser("run", help="Run submodules of this package")
    parse_run.add_argument("run", choices=['twitter', 'cache', 'web'])

    parse_util = subparser.add_parser("util", help="Utilities")
    parse_util.add_argument("-a", metavar="subs", dest="newsubs", nargs='+', type=str, help="Add tracked users")

    return arg_parser


def run(what):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    available_coros = [keep_twits_updated(), keep_cache_updated()]

    if what < 0 or what >= len(available_coros): raise ValueError
    
    coro = loop.create_task(available_coros[what])

    try:
        logger.info("Starting operation")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        coro.cancel()
        loop.stop()
    loop.close()


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    if args.command == "run":
        if args.run == "twitter":
            run(0)
        elif args.run == "cache":
            run(1)
        elif args.run == "web":
            app.run(host="0.0.0.0", debug=True)
    elif args.command == "util":
        if args.newsubs:
            for sub in args.newsubs:
                add_subscription(sub)
    else:
        parser.print_usage()
