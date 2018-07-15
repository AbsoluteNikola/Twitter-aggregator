from configparser import ConfigParser
import os.path as ospath

config = ConfigParser()
config.read('config.conf')

# Variables accessible from other modules
follow_file: str = ospath.expanduser(config['DEFAULT']['follow_file'])

c_key = config['TWITTER']['consumer_key']
c_secret = config['TWITTER']['consumer_secret']
at_key = config['TWITTER']['application_key']
at_secret = config['TWITTER']['application_secret']

dbpath = config['DataBase']['path']
