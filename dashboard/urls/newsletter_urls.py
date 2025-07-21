from django.urls import path
from dashboard.views.newsletter_views import (
    newsletter_list, newsletter_create, newsletter_edit, newsletter_delete,
    newsletter_preview, newsletter_send
)

urlpatterns = [
    path('', newsletter_list, name='list_newsletter'),
    path('create/', newsletter_create, name='create_newsletter'),
    path('<int:pk>/edit/', newsletter_edit, name='edit_newsletter'),
    path('<int:pk>/delete/', newsletter_delete, name='delete_newsletter'),
    path('<int:pk>/preview/', newsletter_preview, name='preview_newsletter'),
    path('<int:pk>/send/', newsletter_send, name='send_newsletter'),
]
