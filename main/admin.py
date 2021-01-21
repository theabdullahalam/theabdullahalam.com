from django.contrib import admin
from .models import Post, PostTopic, PhotoCategory, Photograph
 
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('-modified',)
    search_fields = ('title', 'content',)

@admin.register(PostTopic)
class PostTopicAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    ordering = ('type_name',)
    search_fields = ('type_name',)

@admin.register(PhotoCategory)
class PhotoCategoryAdmin(admin.ModelAdmin):
    list_display = ('categoryname',)
    ordering = ('categoryname',)
    search_fields = ('categoryname',)
 
@admin.register(Photograph)
class PhotographAdmin(admin.ModelAdmin):
    list_display = ('title', 'p_category')
    ordering = ('title',)
    search_fields = ('title', 'p_category',)