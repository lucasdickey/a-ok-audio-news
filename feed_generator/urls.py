from django.urls import path
from .feeds import EnPodcastFeed, ZhPodcastFeed

urlpatterns = [
    path('rss.xml', EnPodcastFeed(), name='rss_en'),
    path('rss-zh.xml', ZhPodcastFeed(), name='rss_zh'),
] 