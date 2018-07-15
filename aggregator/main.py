from .Twit import Twit, Session
from .twitterHandler import get_timeline

def run():
    timeline = get_timeline()
    session = Session()
    for status in timeline:
        twit = Twit(status)
        session.add(twit)

if __name__ == "__main__":
    print("This script cannot be run as is, please run the package itself.")
