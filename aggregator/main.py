from .Twit import Twit, Session
from .twitterHandler import get_timeline
from pprint import pprint

def run():
    timeline = get_timeline()
    pprint(timeline)
    session = Session()
    for status in timeline:
        twit = Twit(status)
        pprint(twit)
        session.add(twit)
    #pprint("NEW\n", session.new)
    session.commit()

if __name__ == "__main__":
    print("This script cannot be run as is, please run the package itself.")
