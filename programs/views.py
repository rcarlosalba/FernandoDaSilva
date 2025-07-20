from django.shortcuts import render

# Create your views here.


def index(request):
    """
    Vista temporal para mostrar que los programas están en construcción.
    """
    return render(request, 'programs/index.html')
