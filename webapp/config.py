from configparser import ConfigParser
from pathlib import Path
import logging

config = ConfigParser()
config.read('config.conf')

# Variables accessible from other modules

c_key = config['TWITTER']['consumer_key']
c_secret = config['TWITTER']['consumer_secret']


# Logging config
simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
#wide_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
debuglog = logging.StreamHandler()
debuglog.setLevel(logging.DEBUG)
debuglog.setFormatter(simple_formatter)

master_logger = logging.getLogger('flaskapp')
master_logger.setLevel(config['DEFAULT']['logging_level'])

master_logger.addHandler(debuglog)
