import os

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse

from .models import Post, PostTopic, Photograph, PhotoCategory


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')
 
def post(request, slug):
    # FETCH OBJ
    post_obj=Post.objects.get(slug = str(slug))
 
    # HUMAN FRIENDLY DATE
    hfr_date = post_obj.created.strftime('%e %b %Y')
    post_obj.hfr_date = hfr_date
 
    # CREATE CONTEXT
    context = {
        'post': post_obj,
    }
 
    # RETURN
    return render(request, 'post.html', context=context)
 
def blog(request, topic='all', pageno=1):
    
    # FETCH THE POSTS
    if topic == 'all':
        posts = Post.objects.all().order_by('-created', 'title')
    else:
        posts = Post.objects.filter(p_type__slug = topic).order_by('-created', 'title')

    # FETCH ALL TOPICS FOR SIDEBAR
    topics = PostTopic.objects.all().order_by('type_name')

    # FETCH CURRENT TOPIC
    topicobj = None

    if topic != 'all':
        topicobj = PostTopic.objects.get(slug = topic)
    else:
        topicobj = {
            'type_name': 'all'
        }
 
    # PAGINATE
    paginator = Paginator(posts, 10)
    page_num = int(pageno)
    page_obj = paginator.get_page(page_num)
    posts = page_obj.object_list
 
    # HUMAN FRIENDLY DATE
    for post in posts:
        hfr_date = post.created.strftime('%e %b %Y')
        post.hfr_date = hfr_date
 
        post.preview = str(post.content).split('</p>')[0].split('<p>')[1]
 
    # SET CONTEXT
    context = {
        'posts': posts,
        'topic': topicobj,
        'topics': topics,
        'pageinator': paginator,
        'page_obj': page_obj,
    }
 
    # RETURN
    return render(request, 'posts.html', context=context)




# CHUNK MAKER FOR SPLITTING INTO COLUMNS
def chunks(lst, n):
    thechunks = []
    length = len(lst)

    # IF PERFECTLY DIVISBLE
    if length % n == 0:
        chunksize = int(length/n)

        for i in range(0, length, chunksize):
            chunk = lst[i:i+chunksize]
            thechunks.append(chunk)

    # IF NOT PERFECTLY DIVISIBLE
    else:
        chunksize = int(length/n)

        # IF THERE ARE LESS ITEMS THAN THE NUMBER OF CHUNKS NEEDED
        # THE RESULT OF ABOVE DIVISION COMES TO ZERO
        if chunksize == 0:
            for item in lst:
                thechunks.append([item])


        # IF THERE ARE MORE ITEMS THAN NUMBER OF CHUNKS,
        # WE NEED TO DISTRIBUTE THE REMAINDER ACROSS THE CHUNKS
        else:

            # FIRST ADD ALL ITEMS 
            # THIS WILL CREATE AN EXTRA CHUNK WITH REMAINDERS
            for i in range(0, length, chunksize):
                chunk = lst[i:i+chunksize]
                thechunks.append(chunk)


            # GET THE EXTRA CHUNK
            extra = thechunks.pop(len(thechunks) - 1)
            
            # DISTRIBUTE IT ACROSS THE CHUNKS
            for i in range(0, len(extra)):
                thechunks[i].append(extra[i])


    return thechunks


def photography(request, category='all'):
    # FETCH ALL PHOTOGRAPHS

    photographs = None

    # FETCH ALL PHOTOGRAPHS
    if category != 'all':
        photographs = Photograph.objects.filter(p_category__slug = category).order_by('-modified', 'title')
    else:
        photographs = Photograph.objects.all().order_by('-modified', 'title')

    # FETCH ALL CATEGORIES
    categories = PhotoCategory.objects.all().order_by('categoryname')

    # SPLIT PHOTOGRAPHS INTO THREE COLUMNS
    parts = list(chunks(photographs, 3))

    # SET CONTEXT
    context = {
        'columns': parts,
        'categories': categories,
        'category': category
    }
 
    # RETURN
    return render(request, 'photography.html', context=context)


def photo(request, slug):

    # FETCH PHOTOGRAPH
    photo = Photograph.objects.get(slug = str(slug))

    # HFR DATE
    photo.hfr_date = photo.created.strftime('%e %b %Y')

    # CATEGORY
    category = photo.p_category

    # RELATED PHOTOGRAPHS
    photographs = Photograph.objects.filter(p_category__slug = category.slug).order_by('-modified', 'title')
    p_list = list(photographs)

    # REMOVE OUR PHOTO FROM THE LIST
    for i in range(0, len(p_list)):
        if p_list[i].id == photo.id:
            p_list.pop(i)
            break

    # INITIALISE parts FOR POSTERITY
    parts = []

    # SPLIT PHOTOGRAPHS INTO THREE COLUMNS
    if len(p_list) > 0:
        parts = list(chunks(p_list, 3))

    # SET CONTEXT
    context = {
        'photo': photo,
        'showrelated': len(p_list) > 0,
        'columns': parts,
        'category': category
    }    
 
    # RETURN
    return render(request, 'photo.html', context=context)
