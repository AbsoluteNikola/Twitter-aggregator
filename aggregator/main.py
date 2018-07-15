from Twit import Twit, Session
from twitterHandler import get_timeline

if __name__ == "__main__":
    timeline = get_timeline()
    session = Session()
    for status in timeline:
        twit = Twit(status)
        session.add(twit)
