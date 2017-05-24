from django.db import models

# Create your models here.


class Article(models.Model):
    url = models.CharField(unique=True, max_length=-1)
    category_id = models.IntegerField()
    media_id = models.IntegerField()
    title = models.TextField()
    content = models.TextField()
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    url = models.CharField(unique=True, max_length=-1)
    category_id = models.IntegerField()
    media_id = models.IntegerField()
    title = models.TextField()
    content = models.TextField()
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'en_articles'

    @classmethod
    def get_article_ids(cls):
        return cls.objects.values_list('article_id', flat=True)


class Categories(models.Model):
    name = models.CharField(unique=True, max_length=-1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'categories'


class Countries(models.Model):
    name = models.CharField(unique=True, max_length=-1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'countries'


class Media(models.Model):
    name = models.CharField(max_length=-1)
    domain = models.CharField(unique=True, max_length=-1)
    country_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'media'
