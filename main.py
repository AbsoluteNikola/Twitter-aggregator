#!/bin/python3
import sys
import asyncio
import uvloop
import argparse
from multiprocessing import Process
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
    if what == 0:
        # p = Process(target=keep_twits_updated)
        keep_twits_updated()
    elif what == 1:
        # p = Process(target=keep_cache_updated)
        keep_cache_updated()
    elif what == 2:
        # p = Process(target=app.run, kwargs={'host': "0.0.0.0", 'debug': True})
        app.run(host="0.0.0.0", debug=True)

    # p.start()
    # try:
    #     p.join()
    # except KeyboardInterrupt:
    #     p.terminate()

if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    if args.command == "run":
        if args.run == "twitter":
            run(0)
        elif args.run == "cache":
            run(1)
        elif args.run == "web":
            run(2)
    elif args.command == "util":
        if args.newsubs:
            for sub in args.newsubs:
                add_subscription(sub)
    else:
        parser.print_usage()
