from configparser import ConfigParser
import os.path as ospath
import logging

config = ConfigParser()
config.read('config.conf')

# Variables accessible from other modules
follow_file: str = ospath.expanduser(config['DEFAULT']['follow_file'])

c_key = config['TWITTER']['consumer_key']
c_secret = config['TWITTER']['consumer_secret']
at_key = config['TWITTER']['application_key']
at_secret = config['TWITTER']['application_secret']
update_delay = config['TWITTER'].getint("update_delay", 3 * 60)

cache_delay = config['cache'].getint('cache_delay', 5 * 60)

dbpath = config['DataBase']['path']

# Logging config
simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
#wide_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
debuglog = logging.StreamHandler()
debuglog.setLevel(logging.DEBUG)
debuglog.setFormatter(simple_formatter)

master_logger = logging.getLogger('aggregator')
master_logger.setLevel(config['DEFAULT']['logging_level'])

master_logger.addHandler(debuglog)

