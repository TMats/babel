from django.db import models
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
        return list(cls.objects.values_list('article_id', flat=True))

    @classmethod
    def get_article(cls, article_id):
        return cls.objects.get(article_id=article_id)


class ArticleCluster(models.Model):
    article_id = models.IntegerField(primary_key=True)
    cluster_id = models.IntegerField()
    created_at = models.DateTimeField(default=now())
    updated_at = models.DateTimeField(default=now())

    class Meta:
        managed = False
        db_table = 'article_clusters'
        # unique_together=('article_id', 'clustered_at')

    @classmethod
    def get_cluster_article(cls, cluster_id):
        return cls.objects.get(cluster_id=cluster_id)


def tokenize_articles():
    article_ids = EnArticle.get_article_ids()
    article_tokens = [tokenize(EnArticle.get_article(article_id).content) for article_id in article_ids]
    return article_tokens, article_ids


def cluster_by_doc2vec(threshold=0.7):
    article_tokens, article_ids = tokenize_articles()

    sentences = [TaggedDocument(words=article_token, tags=[article_id]) for (article_token, article_id) in zip(article_tokens, article_ids)]
    model = Doc2Vec(size=50, min_count=2, iter=55)
    model.build_vocab(sentences)
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)

    matrix = np.eye(len(article_ids))
    for article_id in article_ids:
        similar_article_id, similarity = model.docvecs.most_similar(article_id)[0]
        if similarity >= threshold:
            matrix[article_ids.index(article_id)][article_ids.index(similar_article_id)] = 1
    cluster_num, cluster_ids = connected_components(matrix)
    cluster_ids = list(cluster_ids)

    # save cluster
    for (article_id, cluster_id) in zip(article_ids, cluster_ids):
        article_cluster = ArticleCluster(article_id=article_id, cluster_id=cluster_id)
        article_cluster.save()


def cluster_by_tfidf(threshold=0.5):
    article_ids = EnArticle.get_article_ids()
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
        article_cluster = ArticleCluster(article_id=article_id, cluster_id=cluster_id)
        article_cluster.save()
