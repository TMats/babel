from django.db import models
from django.utils.timezone import now
from clustering.utils import tokenize

from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument


# Create your models here.
class EnArticle(models.Model):
    article_id = models.IntegerField(primary_key=True)
    url = models.CharField(unique=True, max_length=-1)
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

    @classmethod
    def get_article(cls, article_id):
        return cls.objects.get(article_id=article_id)


def tokenize_articles():
    article_ids = EnArticle.get_article_ids()
    article_tokens = [tokenize(EnArticle.get_article(article_id).content) for article_id in article_ids]
    return article_tokens, article_ids


def usedoc2vec():
    article_tokens, article_ids = tokenize_articles()
    trainings = [TaggedDocument(words=article_token, tags=[article_id]) for (article_token, article_id) in zip(article_tokens, article_ids)]
    m = Doc2Vec(documents=trainings, dm=1, size=300, window=8, min_count=10, workers=4)
    m.save("doc2vec.model")
    print(m.docvecs.most_similar(1))

