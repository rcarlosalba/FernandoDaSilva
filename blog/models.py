from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
import re

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(
        blank=True, help_text="Descripción opcional de la categoría")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(
        blank=True, help_text="Descripción opcional de la etiqueta")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    introduction = models.TextField(
        max_length=160, help_text="Brief description for previews and SEO")
    body = models.TextField()
    featured_image = models.ImageField(
        upload_to='blog/images/', blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    reading_time = models.PositiveIntegerField(
        default=0, help_text="Reading time in minutes")
    view_count = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(
        max_length=200, blank=True, help_text="Custom title for SEO")
    meta_description = models.TextField(
        max_length=160, blank=True, help_text="Custom description for SEO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Calculate reading time
        self.reading_time = self.calculate_reading_time()

        super().save(*args, **kwargs)

    def calculate_reading_time(self):
        """Calculate reading time based on word count (200 words per minute)"""
        if self.body:
            # Remove HTML tags and count words
            text = re.sub(r'<[^>]+>', '', self.body)
            word_count = len(text.split())
            return max(1, round(word_count / 200))
        return 1

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def get_meta_title(self):
        return self.meta_title if self.meta_title else self.title

    def get_meta_description(self):
        return self.meta_description if self.meta_description else self.introduction

    def is_published(self):
        return self.status == 'published'

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Comment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('spam', 'Spam'),
    ]

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"

    def is_approved(self):
        return self.status == 'approved'

    def is_reply(self):
        return self.parent is not None

    def get_approved_replies(self):
        return self.replies.filter(status='approved')
