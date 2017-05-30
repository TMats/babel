from django.shortcuts import render
from clustering.models import Article,  JaTitle, EnArticle, Doc2vecArticleCluster, TfidfArticleCluster


# Create your views here
def get_clusters():
    cluster_ids = Doc2vecArticleCluster.get_top_cluster_ids()[0:10]
    # TODO: Refactor below by using queryset join (this needs relation in models)
    clusters = []
    for cluster_id in cluster_ids:
        article_ids = Doc2vecArticleCluster.get_cluster_article_ids(cluster_id)
        cluster_articles = []
        for article_id in article_ids:
            article = Article.get_article(article_id)
            published_at = article.published_at
            url = article.url
            media_id = article.media_id
            title = JaTitle.get_ja_title(article_id)
            article_dict = {'title': title, 'url': url, 'published_at': published_at, 'media_id':media_id}
            cluster_articles.append(article_dict)
        # TODO: 暫定的にヘッドラインは先頭の記事なのでちゃんと選ぶ
        top_article = cluster_articles[0]
        clusters.append({'top_article': top_article, 'cluster_articles': cluster_articles})
    return clusters


def show_index(request):
    clusters = get_clusters()
    template_dict = {'clusters': clusters}
    return render(request, 'clustering/index.html', template_dict)
