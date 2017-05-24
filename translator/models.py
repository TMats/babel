from django.db import models

# Create your models here.


class Article(models.Model):
    id = models.IntegerField
    url = models.CharField
    category_id = models.IntegerField
    media_id = models.IntegerField
    title = models.TextField
    content = models.TextField
    published_at = models.DateTimeField
    created_at = models.DateTimeField
    updated_at = models.DateTimeField

    class Meta:
        managed = False
        db_table = 'articles'


class EnArticles(models.Model):
    article_id = models.IntegerField
    url = models.CharField
    category_id = models.IntegerField
    media_id = models.IntegerField
    title = models.TextField
    content = models.TextField
    published_at = models.DateTimeField
    created_at = models.DateTimeField
    updated_at = models.DateTimeField

    class Meta:
        managed = False
        db_table = 'en_articles'

