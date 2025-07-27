from django.urls import path
from dashboard.views.newsletter_views import (
    newsletter_list, newsletter_create, newsletter_edit, newsletter_delete,
    newsletter_preview, newsletter_send
)

urlpatterns = [
    path('newsletter/', newsletter_list, name='list_newsletter'),
    path('newsletter/create/', newsletter_create, name='create_newsletter'),
    path('newsletter/<int:pk>/edit/', newsletter_edit, name='edit_newsletter'),
    path('newsletter/<int:pk>/delete/',
         newsletter_delete, name='delete_newsletter'),
    path('newsletter/<int:pk>/preview/',
         newsletter_preview, name='preview_newsletter'),
    path('newsletter/<int:pk>/send/', newsletter_send, name='send_newsletter'),
]
