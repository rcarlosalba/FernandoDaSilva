from django.urls import path
from programs import views
from .views import add_session_comment

app_name = 'programs'

urlpatterns = [
    path('programas/', views.index, name='index'),
    path('programas/<int:programa_pk>/',
         views.program_detail, name='program_detail'),
    path('programas/sesion/<int:sesion_pk>/',
         views.session_detail, name='session_detail'),
    path('completar-sesion/<int:sesion_pk>/',
         views.complete_session, name='complete_session'),
    path('programas/<int:programa_pk>/evaluacion-final/',
         views.final_feedback, name='final_feedback'),
]

urlpatterns += [
    path('sesiones/<int:sesion_pk>/comentar/',
         add_session_comment, name='session_add_comment'),
]
