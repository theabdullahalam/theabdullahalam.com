from django.contrib import admin
from .models import Post, PostTopic, PhotoCategory, Photograph, DynamicStuff, Tag, Section, Note, Connection

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    pass

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)
    search_fields = ('title',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)

@admin.register(DynamicStuff)
class DynamicStuffAdmin(admin.ModelAdmin):
    list_display = ('title', 'key',)
    ordering = ('title',)
    search_fields = ('title', 'key', 'value',)

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