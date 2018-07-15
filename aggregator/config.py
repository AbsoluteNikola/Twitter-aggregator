from configparser import ConfigParser
import os.path as ospath

config = ConfigParser()
config.read('config.conf')

# Variables accessible from other modules
follow_file: str = ospath.expanduser(config['DEFAULT']['follow_file'])
