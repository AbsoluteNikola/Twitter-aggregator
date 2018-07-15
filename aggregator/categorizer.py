from nltk.stem.wordnet import WordNetLemmatizer
from rake_nltk import Rake

def get_keywords(text):
    rake = Rake()
    lemm = WordNetLemmatizer()

    rake.extract_keywords_from_text(text)

    keywords = [(score, lemm.lemmatize(word)) for score, word in rake.get_ranked_phrases_with_scores()]

    return keywords
