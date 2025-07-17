from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # URLs públicas
    path('', views.public_event_list, name='event_list'),
    path('evento/<slug:slug>/', views.public_event_detail, name='event_detail'),
    path('categoria/<slug:slug>/',
         views.public_category_detail, name='category_detail'),
    path('evento/<slug:slug>/inscribirse/',
         views.event_registration, name='event_registration'),
    path('inscripcion-exitosa/<int:registration_id>/',
         views.registration_success, name='registration_success'),
]
