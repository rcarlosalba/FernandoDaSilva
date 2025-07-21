from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # Public unsubscribe views
    path('unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
    path('unsubscribe/success/', views.unsubscribe_success,
         name='unsubscribe_success'),
    path('resubscribe/<str:token>/', views.resubscribe, name='resubscribe'),
    path('resubscribe/success/', views.resubscribe_success,
         name='resubscribe_success'),
]
