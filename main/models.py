from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.utils import dateformat
from martor.models import MartorField
import markdown
 
class PostTopic(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    type_name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs):
 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.type_name)
        return super(PostTopic, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog', args=[str(self.slug)])
 
    def __str__(self):
        return str(self.type_name)

class Section(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    name = models.CharField(max_length=250)
    index_template = models.CharField(max_length=250, blank=True, null=True, default=None)
    show_related_notes = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs): 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Section, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('section', args=[str(self.slug)])

    

class Tag(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    name = models.CharField(max_length=250)
    index_template = models.CharField(max_length=250, blank=True, null=True, default=None)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs): 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tag', args=[str(self.slug)])

class Connection(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    to_note = models.ForeignKey("Note", on_delete=models.CASCADE, related_name="connection_to")
    from_note = models.ForeignKey("Note", on_delete=models.CASCADE, related_name="connection_from")

    def __str__(self):
        return str(self.from_note.title + ' -> ' + self.to_note.title)

class Note(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    template = models.CharField(max_length=250, blank=True, null=True, default="note.html")
    image = models.ImageField(upload_to='headers', null=True, blank=True)
    title = models.CharField(max_length=250)
    markdown_content = MartorField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="notes")
    tags = models.ManyToManyField(Tag, related_name="notes")
    created = models.DateTimeField(editable=True, blank=True)
    modified = models.DateTimeField(editable=True, blank=True)
    private = models.BooleanField(default=False)
    show_in_section_list = models.BooleanField(default=False)
    show_related_notes = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs):
        # UPDATE TIMESTAMPS
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.title)

        return_val = super(Note, self).save(*args, **kwargs)

        # make connections
        self.make_connections()

        return return_val
 
    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('note', args=[str(self.slug)])

    def get_sane_description(self, thestring):
        return str(strip_tags(thestring)).replace('&#39;', '\'').replace('&rsquo;', '\'').replace('\n', ' ')

    def modified_human_readable(self):
        return dateformat.format(self.modified, "jS M, Y")

    def created_human_readable(self):
        return dateformat.format(self.created, "jS M, Y")

    def get_html_content(self):
        return markdown.markdown(self.markdown_content)

    def get_paragraph_preview(self):
        preview = ''

        try:
            soup = BeautifulSoup(self.get_html_content(), "html.parser")
            paras = soup.find_all('p')
            if len(paras) > 0:
                first_para = paras[0].string
                words = first_para.split(' ') if first_para is not None else ''
                if len(words) > 0:
                    first_twenty = words[:15]
                    # remove comma from last
                    if first_twenty[-1][-1] == ',':
                        first_twenty[-1] = first_twenty[-1][:-1]

                    # build preview text
                    preview = ' '.join(first_twenty)

                    # add dot dot dot if clipped
                    if len(words) > 15:
                        preview += "..."

        except IndexError as ie:
            print(self.title + ": " + str(ie))
            preview = self.get_html_content()

        return self.get_sane_description(preview)

    def make_connections(self):
        soup = BeautifulSoup(self.get_html_content(), 'html.parser')
        for link in soup.find_all('a'):
            url = urlparse(link.get("href"))
            path = url.path
            parts = path.split("/")
            slug = parts[-1] if parts[-1] != '' else parts[-2]
            to_note = Note.objects.filter(slug = slug).first()

            if to_note is not None:
                connection = Connection.objects.filter(from_note=self, to_note=to_note).first()
                if connection is None:
                    c = Connection(
                        from_note=self,
                        to_note=to_note
                    )
                    c.save()

        
 
class Post(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    header_image = models.ImageField(upload_to='headers', null=True, blank=True)
    title = models.CharField(max_length=250)
    p_type=models.ForeignKey(PostTopic, on_delete=models.CASCADE)
    content = RichTextUploadingField(max_length=14000)
    created = models.DateTimeField(editable=True, blank=True)
    modified = models.DateTimeField(editable=True, blank=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
 
    def save(self, *args, **kwargs):
        # UPDATE TIMESTAMPS
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)
 
    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('post', args=[str(self.slug)])
 
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class PhotoCategory(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    categoryname = models.CharField(max_length=40)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs): 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.categoryname)
        return super(PhotoCategory, self).save(*args, **kwargs)
 
    def __str__(self):
        return str(self.categoryname)

    class Meta:
        verbose_name = 'Photo Category'
        verbose_name_plural = 'Photo Categories'


class Photograph(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    image = models.ImageField(upload_to='photography')
    title = models.CharField(max_length=250)
    p_category=models.ForeignKey(PhotoCategory, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    created = models.DateTimeField(editable=True, blank=True)
    modified = models.DateTimeField(editable=True, blank=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs):
        # UPDATE TIMESTAMPS
        if not self.id or not self.created:
            self.created = timezone.now()
        self.modified = timezone.now()
 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Photograph, self).save(*args, **kwargs)
 
    def __str__(self):
        return str(self.title)

    # def get_absolute_url(self):
    #     return reverse('photograph', args=[str(self.slug)])
 
    class Meta:
        verbose_name = 'Photograph'
        verbose_name_plural = 'Photographs'


class DynamicStuff(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    title = models.CharField(max_length=250)
    key = models.CharField(max_length=250)
    value = RichTextUploadingField(null=True, blank=True)
    image = models.ImageField(upload_to='dynamics', null=True, blank=True)

    class Meta:
        verbose_name = 'Dynamic Thing'
        verbose_name_plural = 'Dynamic Stuff'