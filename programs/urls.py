from django.urls import path
from programs import views

app_name = 'programs'

urlpatterns = [
    path('programas/', views.index, name='index'),
    path('programas/<int:programa_pk>/',
         views.program_detail, name='program_detail'),
    path('programas/sesion/<int:sesion_pk>/',
         views.session_detail, name='session_detail'),
]
