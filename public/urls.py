from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.index, name='index'),
    path('acerca-de/', views.about, name='about'),
    path('servicios/', views.services, name='services'),
    path('testimonios/', views.testimonials, name='testimonials'),
    path('contacto/', views.contact, name='contact'),
]
