from django.db import models
from django.db.models import Count
from django.utils.timezone import now
from clustering.utils import tokenize
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import numpy as np
from scipy.sparse.csgraph import connected_components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOP_WORDS_FOR_TFIDF = [',', '.', "'", '"', "-", '(', ')']


# Create your models here.
class Article(models.Model):
    # id = models.IntegerField(primary_key=True)
    url = models.TextField(unique=True)
    category_id = models.IntegerField()
    # media_id = models.IntegerField()
    media = models.ForeignKey('Media')
    title = models.TextField()
    content = models.TextField()
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())
    image_url = models.TextField()

    class Meta:
        managed = False
        db_table = 'articles'

    @classmethod
    def get_article(cls, article_id):
        return cls.objects.get(id=article_id)


class EnArticle(models.Model):
    # article_id = models.IntegerField(primary_key=True)
    article = models.ForeignKey('Article', primary_key=True)
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
        return cls.objects.values_list('article__id', flat=True).all()

    @classmethod
    def get_article(cls, article_id):
        return cls.objects.get(article__id=article_id)


class JaTitle(models.Model):
    # article_id = models.IntegerField(primary_key=True)
    article = models.ForeignKey('Article', primary_key=True)
    ja_title = models.TextField()
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())

    class Meta:
        managed = False
        db_table = 'ja_titles'

    @classmethod
    def get_ja_title(cls, article_id):
        return cls.objects.get(article__id=article_id).ja_title
        # return cls.objects.select_related('article').get(article_id=article_id).ja_title


class Doc2vecArticleCluster(models.Model):
    # article_id = models.IntegerField(primary_key=True)
    article = models.ForeignKey('Article', primary_key=True)
    cluster_id = models.IntegerField()
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())

    class Meta:
        managed = False
        db_table = 'doc2vec_article_clusters'

    @classmethod
    def get_diverse_cluster_ids(cls):
        return cls.objects.values('cluster_id').annotate(Count('article__media__id', distinct=True)).annotate(Count('article__id')).order_by('article__media__id__count', 'article__id__count').reverse().values_list('cluster_id', flat=True)

    @classmethod
    def get_cluster_articles(cls, cluster_id):
        return cls.objects.filter(cluster_id=cluster_id).order_by('article__published_at').reverse()


class TfidfArticleCluster(models.Model):
    # article_id = models.IntegerField(primary_key=True)
    article = models.ForeignKey('Article', primary_key=True)
    cluster_id = models.IntegerField()
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())

    class Meta:
        managed = False
        db_table = 'tfidf_article_clusters'

    @classmethod
    def get_diverse_cluster_ids(cls):
        return cls.objects.values('cluster_id').annotate(Count('article__media__id', distinct=True)).annotate(Count('article__id')).order_by('article__media__id__count', 'article__id__count').reverse().values_list('cluster_id', flat=True)

    @classmethod
    def get_cluster_articles(cls, cluster_id):
        return cls.objects.filter(cluster_id=cluster_id).order_by('article__published_at').reverse()


class Media(models.Model):
    name = models.TextField()
    domain = models.TextField(unique=True)
    # country_id = models.IntegerField()
    country = models.ForeignKey('Country')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'media'

    @classmethod
    def get_medium(cls, media_id):
        return cls.objects.get(id=media_id)


class Country(models.Model):
    name = models.TextField(unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'countries'


def tokenize_articles():
    article_ids = list(EnArticle.get_article_ids())
    article_tokens = [tokenize(EnArticle.get_article(article_id).content) for article_id in article_ids]
    return article_tokens, article_ids


def cluster_by_doc2vec(threshold=0.75, one_to_many=True, dm=1):
    article_tokens, article_ids = tokenize_articles()

    sentences = [TaggedDocument(words=article_token, tags=[article_id]) for (article_token, article_id) in zip(article_tokens, article_ids)]
    model = Doc2Vec(size=50, min_count=4, iter=80, workers=4)
    model = Doc2Vec(size=50, min_count=4, iter=200, workers=4)
    # model = Doc2Vec(size=100, min_count=2, iter=2000, dm=1, workers=4)
    model.build_vocab(sentences)
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)

    matrix = np.eye(len(article_ids))
    for article_id in article_ids:
        # one-to-many pair logic
        if one_to_many:
            similar_article_id_similarities = model.docvecs.most_similar(article_id)

            for similar_article_id, similarity in similar_article_id_similarities:
                if similarity >= threshold:
                    matrix[article_ids.index(article_id)][article_ids.index(similar_article_id)] = 1
        # one-to-one pair logic
        else:
            similar_article_id, similarity = model.docvecs.most_similar(article_id)[0]
            if similarity >= threshold:
                matrix[article_ids.index(article_id)][article_ids.index(similar_article_id)] = 1
    cluster_num, cluster_ids = connected_components(matrix)
    cluster_ids = list(cluster_ids)

    # save cluster
    for (article_id, cluster_id) in zip(article_ids, cluster_ids):
        article_cluster = Doc2vecArticleCluster(article_id=article_id, cluster_id=cluster_id)
        article_cluster.save()


def cluster_by_tfidf(threshold=0.5):
    article_ids = list(EnArticle.get_article_ids())
    contents = [EnArticle.get_article(article_id).content for article_id in article_ids]
    tfidf_vectorizer = TfidfVectorizer(tokenizer=tokenize, lowercase=False, stop_words=STOP_WORDS_FOR_TFIDF)
    similarity_matrix = np.array(cosine_similarity(tfidf_vectorizer.fit_transform(contents)))

    matrix = np.eye(len(article_ids))
    for i, row in enumerate(similarity_matrix):
        row[i] = 0
        if np.max(row) >= threshold:
            matrix[i, np.argmax(row)] = 1
    cluster_num, cluster_ids = connected_components(matrix)
    cluster_ids = list(cluster_ids)

    # save cluster
    for (article_id, cluster_id) in zip(article_ids, cluster_ids):
        article_cluster = TfidfArticleCluster(article_id=article_id, cluster_id=cluster_id)
        article_cluster.save()
