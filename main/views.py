import os
import random
import uuid
import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from bs4 import BeautifulSoup

from .models import Post, PostTopic, Photograph, PhotoCategory, DynamicStuff, Tag, Section, Note, Connection, Quote



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

# universal context for garden
def get_universal_context():
    notes_to_list = Note.objects.filter(show_in_section_list=True)
    all_sections = Section.objects.all().order_by("name")
    sections = []
    for n in notes_to_list:
        sections.append({
            "name": n.title,
            "slug": n.slug,
            "is_note": True
        })
    for s in all_sections:
        sections.append(s)

    tags = Tag.objects.all().order_by("name")

    return {
        "sections": sections,
        "tags": tags
    }


def get_random_notes(count, exclude_slug=None):
    all = Note.objects.filter(exclude_from_related_notes = False, private=False)
    filtered = all if exclude_slug is None else all.exclude(slug=exclude_slug)
    notes = list(filtered)
    random.shuffle(notes)
    return notes[:count]


# MARTOR UPLOADER
@login_required
def markdown_uploader(request):
    """
    Makdown image upload for locale storage
    and represent as json to markdown editor.
    """
    if request.method == 'POST' and request.is_ajax():
        if 'markdown-image-upload' in request.FILES:
            image = request.FILES['markdown-image-upload']
            image_types = [
                'image/png', 'image/jpg',
                'image/jpeg', 'image/pjpeg', 'image/gif'
            ]
            if image.content_type not in image_types:
                data = json.dumps({
                    'status': 405,
                    'error': _('Bad image format.')
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            if image.size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_MB = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': _('Maximum image file is %(size)s MB.') % {'size': to_MB}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
            tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
            def_path = default_storage.save(tmp_file, ContentFile(image.read()))
            img_url = os.path.join(settings.MEDIA_URL, def_path)

            data = json.dumps({
                'status': 200,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse(_('Invalid request!'))
    return HttpResponse(_('Invalid request!'))

# --------------------- VIEWS -------------------------


def note(request, slug = None):

    m_slug = slug if slug is not None else "home-page"
    note = Note.objects.get(slug = m_slug)

    # related section stuff
    related_section = note.section
    related_notes = related_section.notes.filter(exclude_from_related_notes = False, private = False).exclude(slug = note.slug).exclude(section__slug = "miscellaneous").order_by("title") if (note.show_related_notes and related_section.show_related_notes) else []
    related_section__notes_list__values__slug = related_notes.values("slug")[:5] if related_notes != [] else []
    if len(related_notes) > 6:
        related_section.has_more = True
        related_section.notes_list = related_notes[:5]
    else:
        related_section.notes_list = related_notes

    # related tag stuff
    related_tags = note.tags.all()
    comma_tags = []
    for tag in related_tags:
        related_notes = tag.notes.filter(exclude_from_related_notes = False, private = False).exclude(slug = note.slug).exclude(section__slug = "miscellaneous").exclude(slug__in = related_section__notes_list__values__slug).order_by("title") if (note.show_related_notes and related_section.show_related_notes) else []
        if len(related_notes) > 6:
            tag.has_more = True
            tag.notes_list = related_notes[:5]
        else:
            tag.notes_list = related_notes
        
        soup =  BeautifulSoup('', "html.parser")
        link = soup.new_tag("a")
        link.string = tag.name.lower()
        link["href"] = reverse("tag", kwargs={"slug": tag.slug})
        comma_tags.append(str(link))
    note.comma_tags = ", ".join(comma_tags)

    # related connections stuff
    connection_objects = Connection.objects.filter(to_note=note, to_note__exclude_from_related_notes = False, to_note__private = False).exclude(to_note__section__slug = "miscellaneous")
    connections = []
    connections_has_more = False
    if len(connections) > 6:
        connections = connection_objects[:5]
        connections_has_more = True
    else:
        connections = connection_objects

    # home page stuff
    random_notes = []

    if m_slug == "home-page":
        random_notes = get_random_notes(9, m_slug)

    # quotes
    print(m_slug)
    quotes = Quote.objects.filter(source = note) if m_slug != "quotes" else Quote.objects.all()

    context = {
        "slug": m_slug,
        "note": note,
        "section": section,
        "related_section": related_section,
        "related_tags": related_tags,
        "connections_has_more": connections_has_more,
        "connections": connections,
        "random_notes": random_notes,
        "fullimage": get_full_url(note.image.url) if note.image else "",
        'fullurl': get_full_url(reverse("note", kwargs={"slug": note.slug})),
        "quotes": quotes,
        **get_universal_context()
    }
    return render(request, note.template, context=context)

def section(request, slug):

    section = Section.objects.get(slug=slug)
    notes = Note.objects.filter(section=section, private=False).order_by("title")

    

    context = {
        "index": section,
        "notes": notes,
        "fullimage": "",
        'fullurl': get_full_url(reverse("section", kwargs={"slug": section.slug})),
        **get_universal_context()
    }
    return render(request, section.index_template if section.index_template else 'notelist.html', context=context)

def tag(request, slug):

    tag = Tag.objects.get(slug=slug)
    notes = Note.objects.filter(tags = tag, private=False).order_by("title")

    context = {
        "index": tag,
        "notes": notes,
        "fullimage": "",
        **get_universal_context()
    }
    return render(request, tag.index_template if tag.index_template else 'notelist.html', context=context)



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

def photofolio(request, category='all'):

    # get photographs
    if category == 'all':
        photographs = Photograph.objects.all().order_by('-modified', 'title')
    else:
        photographs = Photograph.objects.filter(p_category__slug = category).order_by('-modified', 'title')

    # get categories
    categories = PhotoCategory.objects.all().order_by('categoryname')

    # build context
    context = {
        "photographs": photographs,
        "categories": categories
    }

    # return context
    return render(request, 'photofolio.html', context=context)

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
    return render(request, 'photography_old.html', context=context)

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
