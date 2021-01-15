from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.urls import reverse
 
class PostTopic(models.Model):
    type_name = models.CharField(max_length=30)
 
    def __str__(self):
        return str(self.type_name)
 
class Post(models.Model):
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