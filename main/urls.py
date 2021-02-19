from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import PostSiteMap, PostTopicSiteMap
from .feeds import LatestPostsFeed
from . import views

sitemaps = {
    'posts': PostSiteMap,
    'types': PostTopicSiteMap
}

urlpatterns = [
 
    path('', views.index, name='index'),

    path('about', views.about, name='about'),
    path('about/', views.about, name='about'),
 
    path('post/<slug:slug>', views.post, name='post'),
    path('post/<slug:slug>/', views.post, name='post'),

    path('blog', views.blog, name='blog'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:topic>', views.blog, name='blog'),
    path('blog/<slug:topic>/', views.blog, name='blog'),
    path('blog/page/<int:pageno>', views.blog, name='blog'),
    path('blog/page/<int:pageno>/', views.blog, name='blog'),
    path('blog/<slug:topic>/page/<int:pageno>', views.blog, name='blog'),
    path('blog/<slug:topic>/page/<int:pageno>/', views.blog, name='blog'),

    path('photography', views.photography, name='photography'),
    path('photography/', views.photography, name='photography'),
    path('photography/category/<slug:category>', views.photography, name='photography'),
    path('photography/category/<slug:category>/', views.photography, name='photography'),

    path('photo/<slug:slug>', views.photo, name='photo'),
    path('photo/<slug:slug>/', views.photo, name='photo'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('feed', LatestPostsFeed(), name='all_posts_feed')
 
]
