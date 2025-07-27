from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'public/index.html')


def about(request):
    return render(request, 'public/about.html')


def services(request):
    return render(request, 'public/services.html')


def testimonials(request):
    return render(request, 'public/testimonials.html')


def contact(request):
    return render(request, 'public/contact.html')
