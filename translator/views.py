from django.shortcuts import render
from translator.models import Article, EnArticle
from babel.settings import STATIC_SETTINGS
# import urllib.request
import requests
import json

BASE_URL = 'https://translation.googleapis.com/language/translate/v2'


# Create your views here.
def get_unranslated_article_ids():
    article_ids = Article.get_article_ids()
    en_article_ids = EnArticle.get_article_ids()
    return list(set(article_ids)-set(en_article_ids))


def translate(text):
    target_url = BASE_URL + '?key=' + STATIC_SETTINGS['api_key'] + '&q=' + text + '&target=en'
    r = requests.get(target_url)
    if r.status_code==200:
        translated_text = json.loads(r.text)['data']['translations'][0]['translatedText']
        return translated_text
    else:
        return None
