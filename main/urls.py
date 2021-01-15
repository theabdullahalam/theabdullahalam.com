from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import PostSiteMap, PostTopicSiteMap
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
    path('blog', views.blog, name='blog'),
    path('blog/', views.blog, name='blog'),
    path('blog/page/<int:pageno>', views.blog, name='blog'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
 
]
