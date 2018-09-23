import re
from html import unescape
from unicodedata import normalize
from nltk.stem.wordnet import WordNetLemmatizer
from rake_nltk import Rake
from logging import getLogger

logger = getLogger("aggregator.categorizer")

def preprocess_text(txt: str):
#    logger.debug("%-10s: %s" % ("Got", txt))
    txt = unescape(txt)   # Remove html encoded chars
#    logger.debug("%-10s: %s" % ("Escaped", txt))
    txt = normalize("NFKD", txt)   # Remove unicode special characters
#    logger.debug("%-10s: %s" % ("Normalized", txt))
    txt = [re.sub(r"[^A-Za-z0-9]*", r"", word) for word in txt.split()]
#    logger.debug("%-10s: %s" % ("After re", txt))
    txt = ' '.join(txt)
    return txt

def get_keywords(text):
    rake = Rake()
    lemm = WordNetLemmatizer()

    sanitized = preprocess_text(text)
    logger.debug("Sanitized: %s" % sanitized)

    rake.extract_keywords_from_text(sanitized)

    keywords = [(score, lemm.lemmatize(word)) for score, word in rake.get_ranked_phrases_with_scores()]

    return keywords
