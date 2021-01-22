from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.sites.models import Site
 
class PostTopic(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=1, editable=False)
    type_name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs):
 
        # GENERATE SLUG
        if not self.slug:
            self.slug = slugify(self.type_name)
        return super(PostTopic, self).save(*args, **kwargs)
 
    def __str__(self):
        return str(self.type_name)
 
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