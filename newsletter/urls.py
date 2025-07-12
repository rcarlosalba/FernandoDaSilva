from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # Dashboard views (manager required)
    path('', views.newsletter_list, name='list'),
    path('create/', views.newsletter_create, name='create'),
    path('<int:pk>/edit/', views.newsletter_edit, name='edit'),
    path('<int:pk>/delete/', views.newsletter_delete, name='delete'),
    path('<int:pk>/preview/', views.newsletter_preview, name='preview'),
    path('<int:pk>/send/', views.newsletter_send, name='send'),
    
    # Public unsubscribe views
    path('unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
    path('unsubscribe/success/', views.unsubscribe_success, name='unsubscribe_success'),
    path('resubscribe/<str:token>/', views.resubscribe, name='resubscribe'),
    path('resubscribe/success/', views.resubscribe_success, name='resubscribe_success'),
]