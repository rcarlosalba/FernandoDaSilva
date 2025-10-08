from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.index, name='index'),
    path('acerca-de/', views.about, name='about'),
    path('servicios/', views.services, name='services'),
    path('testimonios/', views.testimonials, name='testimonials'),
    path('libros/', views.BookLandingView.as_view(), name='books'),
    path('download-chapter/', views.download_chapter, name='download_chapter'),
    path('contacto/', views.contact, name='contact'),
]
