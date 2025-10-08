import os
from django.shortcuts import render
from django.views.generic import FormView
from django.http import FileResponse, JsonResponse
from django.conf import settings
from django.contrib import messages

from accounts.utils import send_book_download_email
from .forms import BookSubscriberForm

# Create your views here.


def index(request):
    return render(request, 'public/index.html')


def about(request):
    return render(request, 'public/about.html')


def services(request):
    return render(request, 'public/services.html')


def testimonials(request):
    return render(request, 'public/testimonials.html')


class BookLandingView(FormView):
    """
    Landing page for book 'Camino, Verdad y Vida'.
    Allows users to download first chapter by providing email.
    """

    template_name = 'public/book_landing.html'
    form_class = BookSubscriberForm

    def form_valid(self, form):
        """
        Creates subscriber and triggers PDF download + email.
        """
        user = form.save()

        # Send email with profile completion link
        send_book_download_email(user.email, user.pk, self.request)

        # Mark download as successful in session
        self.request.session['book_downloaded'] = True

        # Prepare PDF for download
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'books', 'capitulo1.pdf')

        # Handle AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if os.path.exists(pdf_path):
                return JsonResponse({
                    'success': True,
                    'download_url': '/download-chapter/',
                    'message': '¡Descarga iniciada! Revisa tu email para completar tu perfil.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'El archivo no se encontró. Por favor contacta al administrador.'
                }, status=404)

        # Handle regular form submission (fallback)
        if os.path.exists(pdf_path):
            try:
                pdf_file = open(pdf_path, 'rb')
                response = FileResponse(
                    pdf_file, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="Capitulo1_CaminoVerdadVida.pdf"'

                messages.success(
                    self.request,
                    '¡Descarga iniciada! Revisa tu email para completar tu perfil y acceder a más contenido.'
                )

                return response
            except Exception as e:
                messages.error(
                    self.request,
                    f'Error técnico: {str(e)}'
                )
                return self.render_to_response(self.get_context_data(form=form))
        else:
            messages.error(
                self.request,
                'Error al descargar el capítulo. El archivo no se encontró. Por favor contacta al administrador.'
            )
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        """
        Handles form errors.
        """
        # Handle AJAX request
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Adds book information to context.
        """
        context = super().get_context_data(**kwargs)
        context['book_title'] = 'Camino, Verdad y Vida'
        context['book_subtitle'] = 'Filosofía Sapiencial con olor a Chamamé'
        context['author'] = 'Fernando Da Silva'
        context['book_downloaded'] = self.request.session.get(
            'book_downloaded', False)
        return context


def contact(request):
    return render(request, 'public/contact.html')


def download_chapter(request):
    """
    Endpoint to download the PDF file.
    Only accessible if user has already submitted the form.
    """
    if not request.session.get('book_downloaded', False):
        return JsonResponse({
            'success': False,
            'error': 'No autorizado'
        }, status=403)

    pdf_path = os.path.join(settings.MEDIA_ROOT, 'books', 'capitulo1.pdf')

    if os.path.exists(pdf_path):
        pdf_file = open(pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Capitulo1_CaminoVerdadVida.pdf"'
        return response
    else:
        return JsonResponse({
            'success': False,
            'error': 'Archivo no encontrado'
        }, status=404)
