from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'view_count', 'reading_time', 'created_at']
    list_filter = ['status', 'category', 'tags', 'created_at', 'author']
    search_fields = ['title', 'introduction', 'body']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['reading_time', 'view_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'slug', 'introduction', 'body', 'featured_image']
        }),
        ('Publication', {
            'fields': ['status', 'author', 'category', 'tags']
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse']
        }),
        ('Statistics', {
            'fields': ['reading_time', 'view_count', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new post
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'status', 'is_reply', 'created_at']
    list_filter = ['status', 'created_at', 'post__category']
    search_fields = ['content', 'author__email', 'post__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['post', 'author', 'parent']
    actions = ['approve_comments', 'mark_as_spam']

    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Reply'

    def approve_comments(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = 'Approve selected comments'

    def mark_as_spam(self, request, queryset):
        queryset.update(status='spam')
        self.message_user(request, f'{queryset.count()} comments marked as spam.')
    mark_as_spam.short_description = 'Mark selected comments as spam'

    fieldsets = [
        ('Comment Details', {
            'fields': ['post', 'author', 'content', 'status', 'parent']
        }),
        ('Timestamps', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
