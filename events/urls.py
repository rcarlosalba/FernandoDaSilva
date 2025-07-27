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

    # URLs de encuestas públicas
    path('encuesta/<str:token>/', views.survey_response, name='survey_response'),
    path('encuesta/gracias/', views.survey_thanks, name='survey_thanks'),
    path('encuesta/expirada/', views.survey_expired, name='survey_expired'),
]
