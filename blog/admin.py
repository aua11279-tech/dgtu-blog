from django.contrib import admin
from .models import Article, Tag, Profile


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'is_published')
    list_filter = ('is_published', 'tags', 'published_date')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {}
    date_hierarchy = 'published_date'
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at',)