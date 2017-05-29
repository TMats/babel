from django.db import models
from django.utils.timezone import now
from translator.utils import translate


# Create your models here.
class Article(models.Model):
    url = models.TextField(unique=True)
    category_id = models.IntegerField()
    media_id = models.IntegerField()
    title = models.TextField()
    content = models.TextField()
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())

    class Meta:
        managed = False
        db_table = 'articles'

    @classmethod
    def get_article_ids(cls):
        return cls.objects.values_list('id', flat=True)

    @classmethod
    def get_article(cls, id):
        return cls.objects.get(id=id)


class EnArticle(models.Model):
    article_id = models.IntegerField(primary_key=True)
    url = models.TextField(unique=True)
    category_id = models.IntegerField()
    media_id = models.IntegerField()
    title = models.TextField()
    content = models.TextField()
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())

    class Meta:
        managed = False
        db_table = 'en_articles'

    @classmethod
    def get_article_ids(cls):
        return cls.objects.values_list('article_id', flat=True)


class JaTitle(models.Model):
    article_id = models.IntegerField(primary_key=True)
    ja_title = models.TextField()
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())

    class Meta:
        managed = False
        db_table = 'ja_titles'

    @classmethod
    def get_article_ids(cls):
        return cls.objects.values_list('article_id', flat=True)


class Category(models.Model):
    name = models.TextField(unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'categories'


class Country(models.Model):
    name = models.TextField(unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'countries'


class Medium(models.Model):
    name = models.TextField()
    domain = models.TextField(unique=True)
    country_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'media'


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
    if media_id in (1, 4, 5, 8, 9, 10):
        title = translate(article.title)
        content = translate(article.content)
    # English media
    else:
        title = article.title
        content = article.content
    # insert article to DB
    if title and content:
        en_article = EnArticle(article_id=article_id, url=url, category_id=category_id, media_id=media_id, title=title, content=content, published_at=published_at)
        en_article.save()
    else:
        print("article was not translated")


def translate_untranslated_articles():
    article_ids = get_untranslated_article_ids()
    # newer article is to be processed prior
    for article_id in sorted(article_ids, reverse=True):
        save_translated_articles(article_id)
        print(article_id)


def get_untranslated_title_article_ids():
    en_article_ids = EnArticle.get_article_ids()
    title_article_ids = JaTitle.get_article_ids()
    return list(set(en_article_ids)-set(title_article_ids))


def translate_titles():
    article_ids = get_untranslated_title_article_ids()
    for article_id in article_ids:
        article = Article.get_article(article_id)
        # TODO: Stop HardCoding media_ids
        # Japanese Media
        if article.media_id in (1, ):
            title = article.title
        # Not Japanese Media
        else:
            title = translate(article.title, target_language='ja')

        if title:
            ja_title = JaTitle(article_id=article_id, ja_title=title)
            ja_title.save()
        else:
            print("title was not translated")
