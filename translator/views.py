from django.shortcuts import render
from translator.models import Article, EnArticle
from translator.utils import translate


# Create your views here.
def get_untranslated_article_ids():
    article_ids = Article.get_article_ids()
    en_article_ids = EnArticle.get_article_ids()
    return list(set(article_ids)-set(en_article_ids))


def save_translated_articles(article_id):
    article = Article.get_article(article_id)
    url = article.url
    category_id = article.category_id
    media_id = article.media_id
    published_at = article.published_at
    # not English media
    # TODO: Stop HardCoding media_ids
    if media_id in (1,4,5):
        title = translate(article.title)
        content = translate(article.content)
    # English media
    else:
        title = article.title
        content = article.content
    # insert article to DB
    if title and content:
        en_article = EnArticle(article_id=article_id, url= url, category_id=category_id, media_id=media_id, title=title, content=content, published_at=published_at)
        en_article.save()


def translate_untranslated_articles():
    article_ids = get_untranslated_article_ids()
    for article_id in article_ids:
        save_translated_articles(article_id)
        print(article_id)
