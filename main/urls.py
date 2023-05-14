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
 
    path('', views.note, name='index'),

    path('note/<slug:slug>', views.note, name='note'),
    path('note/<slug:slug>/', views.note, name='note'),

    path('section/<slug:slug>', views.section, name='section'),
    path('section/<slug:slug>/', views.section, name='section'),

    path('tag/<slug:slug>', views.tag, name='tag'),
    path('tag/<slug:slug>/', views.tag, name='tag'),
    
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

    path('photography', views.photofolio, name='photography'),
    path('photography/', views.photofolio, name='photography'),
    path('photography/category/<slug:category>', views.photography, name='photography'),
    path('photography/category/<slug:category>/', views.photography, name='photography'),

    path('photo/<slug:slug>', views.photo, name='photo'),
    path('photo/<slug:slug>/', views.photo, name='photo'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('feed', LatestPostsFeed(), name='all_posts_feed'),

    path("api/uploader/", views.markdown_uploader, name="markdown_uploader_page")
 
]
