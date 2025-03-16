from django.contrib import admin
from django.utils.safestring import mark_safe 

from .models import Category, Location, Post, Comment


@admin.action(description='Опубликовать выбранные посты')
def activate_publish(model, request, obj):
    obj.update(is_published=True)


@admin.action(description='Скрыть выбранные посты')
def deactivate_publish(model, request, obj):
    obj.update(is_published=False)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'description',
        'created_at',
        'slug'
    )
    search_fields = ('title', 'description')
    list_filter = ('is_published',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published'
    )
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'category',
        'text',
        'pub_date',
        'author',
        'location',
        'show_image',
    )
    list_editable = ('is_published', 'location')
    search_fields = ('title', 'author', 'category', 'location')
    list_filter = ('is_published', 'category', 'author',)
    list_per_page = 20
    actions = (activate_publish, deactivate_publish)
    def show_image(self, obj):
        if obj.image:  # Проверяем, есть ли изображение
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="60" />')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'post',
        'created_at'
    )
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('created_at', 'author')
    ordering = ('-created_at',)
    fields = ('text', 'post', 'author', 'created_at')
    readonly_fields = ('created_at',)
