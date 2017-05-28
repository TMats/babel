from babel.settings import STATIC_SETTINGS
import requests
import json
# import re

BASE_URL = 'https://translation.googleapis.com/language/translate/v2'


def translate(text):
    target_url = BASE_URL + '?key=' + STATIC_SETTINGS['api_key'] + '&q=' + text + '&target=en'
    print(target_url)
    r = requests.get(target_url)
    if r.status_code==200:
        translated_text = json.loads(r.text)['data']['translations'][0]['translatedText']
        return translated_text
    else:
        print('API Error')
        return None


# TODO: Translate articles whose number of text is more than 900
# def split_text(text):
#     splited_text = re.split('[.。]')
