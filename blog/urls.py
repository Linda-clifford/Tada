from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ArticleSitemap

sitemaps = {'articles': ArticleSitemap}


urlpatterns = [
    path('', views.home, name='home'),
    path('articles/<slug:slug>/', views.article_detail, name="article_detail"),
    path('source/<str:source>/', views.source_articles, name='source_articles'),
    path('category/<str:category>/', views.category_articles, name='category_articles'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('search/', views.search_articles, name='search_articles'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),

]