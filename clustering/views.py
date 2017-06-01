from django.shortcuts import render
from clustering.models import Article,  JaTitle, EnArticle, Doc2vecArticleCluster, TfidfArticleCluster
import re


# Create your views here
def process_article_dict(article):
    if article:
        article_id = article.id
        published_at = article.published_at
        url = article.url
        media_name = article.media.name
        country_id = article.media.country.id
        image_url = article.image_url
        title = JaTitle.get_ja_title(article.id)
        splitted_content = re.split('[.。]', article.content)
        if len(article.content) <= 3:
            content_intro = article.content
        else:
            content_intro = '. '.join(splitted_content[0:3]) + '. ...'
        article_dict = {'article_id': article_id, 'title': title, 'content_intro': content_intro, 'url': url, 'published_at': published_at, 'media_name': media_name, 'country_id': country_id, 'image_url':image_url}
        return article_dict


def get_clusters(article_cluster_class):
    cluster_ids = article_cluster_class.get_diverse_cluster_ids()[0:20]
    clusters = []
    for cluster_id in cluster_ids:
        articles = article_cluster_class.get_cluster_articles(cluster_id)
        ja_articles = articles.filter(article__media__country=1)
        if ja_articles:
            top_article = process_article_dict(ja_articles.order_by('article__published_at')[0].article)
        else:
            top_article = process_article_dict(articles.order_by('article__published_at')[0].article)
        cluster_articles = [process_article_dict(a.article) for a in articles.exclude(article__id=top_article['article_id'])]
        clusters.append({'top_article': top_article, 'cluster_articles': cluster_articles})
    return clusters


def show_index(request):
    clusters = get_clusters(Doc2vecArticleCluster)
    template_dict = {'clusters': clusters}
    return render(request, 'clustering/index.html', template_dict)


def show_tfidf_index(request):
    clusters = get_clusters(TfidfArticleCluster)
    template_dict = {'clusters': clusters}
    return render(request, 'clustering/index.html', template_dict)
