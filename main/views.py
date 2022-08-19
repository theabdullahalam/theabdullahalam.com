import os

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import strip_tags

from .models import Post, PostTopic, Photograph, PhotoCategory, DynamicStuff, Tag, Section, Note



# --------------------- HELPERS -------------------------

def get_sane_description(thestring):
    return str(strip_tags(thestring)).replace('&#39;', '\'').replace('&rsquo;', '\'').replace('\n', ' ')


def get_protocol():
    if os.environ.get('DEBUG').lower() == 'true':
        return 'http'
    else:
        return 'https'

def get_full_url(ending):
    return '%s://%s%s' % (get_protocol(), Site.objects.get_current().domain, ending)


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

def get_paragraph_preview(content):
    preview = ''

    try:
        first_para = str(content).split('</p>')[0].split('<p>')[1]
        first_twenty = first_para.split(' ')[:35]
        # remove comma from last
        if first_twenty[-1][-1] == ',':
            first_twenty[-1] = first_twenty[-1][:-1]

        preview = '{}...'.format(' '.join(first_twenty), '...')
    except IndexError as ie:
        print(str(ie))
        preview = content

    return preview

def get_universal_context():
    sections = Section.objects.all()
    tags = Tag.objects.all()

    return {
        "sections": sections,
        "tags": tags
    }


# --------------------- VIEWS -------------------------





def note(request, slug):
    context = {
        "title": "Digital Garden"
    }
    return render(request, 'note.html', context=context)

def section(request, slug):

    section = Section.objects.get(slug=slug)
    notes = Note.objects.filter(section=section)

    print(section)

    context = {
        "index": section,
        "notes": notes,
        **get_universal_context()
    }
    return render(request, 'notelist.html', context=context)

def tag(request, slug):

    tag = Tag.objects.get(slug=slug)
    notes = Note.objects.filter(tags = tag)

    context = {
        "index": tag,
        "notes": notes,
        **get_universal_context()
    }
    return render(request, 'notelist.html', context=context)



def index(request):

    # GET BIO
    bio = DynamicStuff.objects.get(key='index-page-bio')

    # GET DP
    dp = DynamicStuff.objects.get(key='dp')

    # GET LATEST 9 POSTS
    latestposts = Post.objects.all().order_by('-created', 'title')[:9]
    for post in latestposts:
        hfr_date = post.created.strftime('%e %b %Y')
        post.hfr_date = hfr_date
 
        post.preview = str(post.content).split('</p>')[0].split('<p>')[1]

    # MAIN POST AND SIDEBAR POSTS
    mainposts = latestposts[:4]
    sidebarposts = latestposts[4:]

    # GET LATEST NINE PHOTOGRAPHS
    photographs = Photograph.objects.all().order_by('-created', 'title')[:9]
    parts = list(chunks(photographs, 3))

    # SET CONTEXT
    context = {
        'mainposts': mainposts,
        'sidebarposts': sidebarposts,
        'columns': parts,
        'bio': bio,
        'description' : get_sane_description(str(bio.value)),
        'fullurl': get_full_url(reverse('index')),
        'fullimage': get_full_url(dp.image.url),
        'dp': dp
    }

    return render(request, 'index.html', context=context)

def about(request):
    
    # GET BIO
    bio = DynamicStuff.objects.get(key='about-page-bio')

    # GET DP
    dp = DynamicStuff.objects.get(key='dp')

    context = {
        'bio': bio,
        'description': get_sane_description(str(bio.value)),
        'fullurl': get_full_url(reverse('about')),
        'fullimage': get_full_url(dp.image.url),
        'dp': dp
    }

    return render(request, 'about.html', context=context)
 
def post(request, slug):
    # FETCH OBJ
    post_obj=Post.objects.get(slug = str(slug))
 
    # HUMAN FRIENDLY DATE
    hfr_date = post_obj.created.strftime('%e %b %Y')
    post_obj.hfr_date = hfr_date




    # SIDEBAR STUFF

    # RELATED POSTS (SAME TOPIC)
    relatedposts = Post.objects.filter(p_type__slug = post_obj.p_type.slug).exclude(id = post_obj.id).order_by('-created', 'title')[:5]
    for post in relatedposts:
        hfr_date = post.created.strftime('%e %b %Y')
        post.hfr_date = hfr_date
 
        post.preview = str(post.content).split('</p>')[0].split('<p>')[1]

    # LATEST POSTS
    latestposts = Post.objects.all().exclude(id = post_obj.id).order_by('-created', 'title')[:5]
    for post in latestposts:
        hfr_date = post.created.strftime('%e %b %Y')
        post.hfr_date = hfr_date
 
        post.preview = str(post.content).split('</p>')[0].split('<p>')[1]


    # FULL IMAGE URL
    fullimage = get_full_url(static('img/favicon.png'))
    if post_obj.header_image != '':
        fullimage = get_full_url(post_obj.header_image.url)

 
    # CREATE CONTEXT
    context = {
        'post': post_obj,
        'related': relatedposts,
        'latest': latestposts,
        'description': get_paragraph_preview(post_obj.content),
        'fullimage': fullimage,
        'fullurl': get_full_url(reverse('post', args=[slug]))
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

    # TWITTER IMAGE
    fullimage = get_full_url(static('img/favicon.png'))


    # FIGURE OUT URL
    fullurl = ''

    if topic == 'all':
        if pageno == 1:
            fullurl = get_full_url(reverse('blog'))
        else:
            fullurl = get_full_url(reverse('blog', args=[pageno]))
    else:
        if pageno == 1:
            fullurl = get_full_url(reverse('blog', args=[topic]))
        else:
            fullurl = get_full_url(reverse('blog', args=[topic, pageno]))
 
    # SET CONTEXT
    context = {
        'posts': posts,
        'topic': topicobj,
        'topics': topics,
        'pageinator': paginator,
        'page_obj': page_obj,
        'description': get_sane_description(str(DynamicStuff.objects.get(key='blog-description').value)),
        'fullurl': fullurl,
        'fullimage': fullimage
    }
 
    # RETURN
    return render(request, 'posts.html', context=context)

def photography(request, category='all'):
    
    photolist = None

    # FETCH ALL CATEGORIES
    categories = PhotoCategory.objects.all().order_by('categoryname')

    # FETCH PHOTOGRAPHS
    if category != 'all':
        photolist = Photograph.objects.filter(p_category__slug = category).order_by('-modified', 'title')
    else:
        # REARRANGE PHOTOGRAPHS IN SEQUENCE 

        #THIS IS SIMPLAY A LIST OF LISTS OF PHOTOGRAPHS, EACH LIST WITH PHOTOGRAPHS OF A PARTICULAR CATEGORY    
        catlist_of_photolists = [] 
        for c in categories:
            catlist_of_photolists.append(
                Photograph.objects.filter(p_category__slug = c.slug).order_by('-modified', 'title')
            )

        # NOW WE LOOP THROUGH THAT LIST AND ADD PICS ONE BY ONE INTO A NEW LIST
        pointer = 0
        photolist = []
        somevar = True

        # GET TOTAL NO. OF PICTURES
        totalpics = 0
        for c in catlist_of_photolists:
            totalpics += len(c)

        for i in range(0, totalpics):
            for c in catlist_of_photolists:
                if pointer < len(c):
                    photolist.append(c[pointer])
                    added = True

            pointer += 1
            
    # endif lol



    # SPLIT PHOTOGRAPHS INTO THREE COLUMNS
    parts = list(chunks(photolist, 3))

    # GET BIO
    description = get_sane_description(str(DynamicStuff.objects.get(key = 'photography-description').value))

    # SET URL DEPENDING ON CATEGORY
    fullurl = ''
    if category == 'all':
        fullurl = get_full_url(reverse('photography'))
    else:
        fullurl = get_full_url(reverse('photography', args=[category]))

    # SET CONTEXT
    context = {
        'columns': parts,
        'categories': categories,
        'category': category,
        'description': description,
        'fullimage': get_full_url(photolist[0].image.url),
        'fullurl': fullurl
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
    twoparts = []

    # SPLIT PHOTOGRAPHS INTO THREE COLUMNS
    if len(p_list) > 0:
        parts = list(chunks(p_list, 3))

    # SPLIT PHOTOGRAPHS INTO TWO COLUMNS FOR MOBILE
    if len(p_list) > 0:
        twoparts = list(chunks(p_list, 2))

    # SET CONTEXT
    context = {
        'photo': photo,
        'showrelated': len(p_list) > 0,
        'columns': parts,
        'twocolumns': twoparts,
        'category': category,
        'description': get_sane_description(str(photo.content)),
        'fullurl': get_full_url(reverse('photo', args=[slug])),
        'fullimage': get_full_url(photo.image.url)
    }    
 
    # RETURN
    return render(request, 'photo.html', context=context)
