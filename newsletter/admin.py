from django.contrib import admin
from .models import Newsletter, Subscriber


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at', 'sent_date']
    list_filter = ['status', 'created_at', 'sent_date']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'sent_date']
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.status != 'draft':
            readonly_fields.extend(['title', 'content'])
        return readonly_fields


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_subscribed', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_subscribed', 'subscribed_at', 'unsubscribed_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['unsubscribe_token', 'subscribed_at', 'unsubscribed_at']
