from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post
from django.urls import reverse

class LatestPostsFeed(Feed):
    title = 'Abdullah Alam Latest Posts'
    link = '/feed'
    description = "RSS Feed for latest posts from Abdullah"

    def items(self):
        return Post.objects.order_by('-created', 'title')[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):


        preview = ''
        content = item.content

        try:
            first_para = str(content).split('</p>')[0].split('<p>')[1]
            first_twenty = first_para.split(' ')[:20]
            # remove comma from last
            if first_twenty[-1][-1] == ',':
                first_twenty[-1] = first_twenty[-1][:-1]

            preview = '{}...'.format(' '.join(first_twenty), '...')
        except IndexError as ie:
            print(str(ie))
            preview = content

        return preview