from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

CUSTOM_STOP_WORDS = ['quot', 'Xinhua', ';', '&', '.&', ',&', '&#']


def tokenize(text):
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english')) | set(CUSTOM_STOP_WORDS)
    text_tokens = [stemmer.stem(token) for token in wordpunct_tokenize(text) if token.lower() not in stop_words]
    return text_tokens
