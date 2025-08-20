from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView
)
from django.contrib import messages
from django.core.signing import BadSignature, SignatureExpired, Signer, TimestampSigner
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView, FormView
from django.views import View
from django.utils import timezone

from constants.constant import UserRoles
from .forms import (
    CompleteProfileForm,
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    ProfileEditForm,
    SubscriberRegistrationForm,
)
from .utils import send_welcome_subscriber_email, send_welcome_member_email, send_account_deactivation_email, send_password_reset_email
from .models import Profile, User


class SubscriberRegistrationView(CreateView):
    """
    Handles the registration of a new subscriber.
    A welcome email should be sent with a unique link to complete the profile.
    """

    model = User
    form_class = SubscriberRegistrationForm
    template_name = "accounts/registration/register_subscriber.html"
    success_url = reverse_lazy("accounts:registration_done")

    def form_valid(self, form):
        user = form.save()
        send_welcome_subscriber_email(user.email, user.pk, self.request)
        return super().form_valid(form)


class RegistrationDoneView(TemplateView):
    """
    Shows a confirmation message after a subscriber has registered.
    """

    template_name = "accounts/registration/registration_done.html"


class CompleteProfileView(UpdateView):
    """
    Allows a subscriber to complete their profile, set a password,
    and become a member.
    """

    model = Profile
    form_class = CompleteProfileForm
    template_name = "accounts/registration/complete_profile.html"
    success_url = reverse_lazy("public:index")  # Or a welcome page

    def get_object(self, queryset=None):
        """
        Retrieves the user object based on the signed ID from the URL,
        then returns the associated profile.
        """
        signed_user_id = self.kwargs.get("signed_user_id")
        signer = Signer()
        try:
            user_id = signer.unsign(signed_user_id)
            self.user_instance = get_object_or_404(User, pk=user_id)
            return self.user_instance.profile
        except (BadSignature, SignatureExpired):
            # Handle invalid or expired link, maybe redirect to an error page
            # For now, this will raise a 404, which is acceptable.
            return None

    def form_valid(self, form):
        """
        If the form is valid, it sets the user's password, updates the role,
        and logs the user in.
        """
        profile = form.save()
        user = profile.user
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.role = UserRoles.MEMBER
        user.save()

        send_welcome_member_email(user.email)

        login(self.request, user)
        return redirect(self.get_success_url())


class CustomLoginView(LoginView):
    """
    Custom login view using our Spanish-labeled form.
    """
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        """
        Redirect users based on their role after successful login.
        """
        user = self.request.user

        if user.role == UserRoles.MANAGER:
            return reverse_lazy('dashboard:dashboard')
        elif user.role == UserRoles.STUDENT:
            return reverse_lazy('programs:index')
        else:
            # SUBSCRIBER, MEMBER, ASSISTANT -> public:index
            return reverse_lazy('public:index')

    def form_valid(self, form):
        """
        Log the user in and show a success message.
        """
        response = super().form_valid(form)
        messages.success(
            self.request, f'¡Bienvenido de vuelta, {self.request.user.email}! Has iniciado sesión correctamente.')
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    """
    Displays the user's profile page.
    """
    model = Profile
    template_name = "accounts/profile/profile.html"
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """
        Returns the profile of the currently logged-in user.
        """
        return self.request.user.profile


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Allows the logged-in user to edit their own profile.
    """
    model = Profile
    form_class = ProfileEditForm
    template_name = 'accounts/profile/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        """
        Returns the profile of the currently logged-in user.
        """
        return self.request.user.profile


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """
    Handles the account deletion request.
    The user is marked as inactive instead of being physically deleted.
    """
    model = User
    template_name = 'accounts/profile/account_delete.html'
    success_url = reverse_lazy('public:index')

    def get_object(self, queryset=None):
        """
        Returns the currently logged-in user.
        """
        return self.request.user

    def form_valid(self, form):
        """
        Instead of deleting the user, we mark it as inactive.
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        send_account_deactivation_email(user.email)
        logout(self.request)
        return redirect(self.get_success_url())


class CustomLogoutView(View):
    """
    Custom logout view that shows a success message.
    """

    def get(self, request):
        """
        Log the user out and show a success message.
        """
        if request.user.is_authenticated:
            user_email = request.user.email
            logout(request)
            messages.success(
                request, f'Has cerrado sesión correctamente. ¡Esperamos verte pronto!')
        return redirect('public:index')


class PasswordResetRequestView(FormView):
    """
    Vista para solicitar el restablecimiento de contraseña.
    """
    
    form_class = PasswordResetRequestForm
    template_name = "accounts/password/password_reset_request.html"
    success_url = reverse_lazy("accounts:password_reset_sent")
    
    def form_valid(self, form):
        """
        Envía el email de restablecimiento de contraseña.
        """
        email = form.cleaned_data["email"]
        user = User.objects.get(email=email, is_active=True)
        send_password_reset_email(user.email, user.pk, self.request)
        return super().form_valid(form)


class PasswordResetSentView(TemplateView):
    """
    Vista de confirmación después de enviar el email de reset.
    """
    
    template_name = "accounts/password/password_reset_sent.html"


class PasswordResetConfirmView(FormView):
    """
    Vista para confirmar el restablecimiento de contraseña con token.
    """
    
    form_class = PasswordResetConfirmForm
    template_name = "accounts/password/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")
    
    def get_user(self):
        """
        Obtiene el usuario basado en el token firmado.
        """
        signed_user_id = self.kwargs.get("signed_user_id")
        signer = TimestampSigner()
        try:
            # Verificar que el token no haya expirado (3 horas = 10800 segundos)
            user_id = signer.unsign(signed_user_id, max_age=10800)
            return get_object_or_404(User, pk=user_id, is_active=True)
        except (BadSignature, SignatureExpired):
            return None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica la validez del token antes de procesar la vista.
        """
        self.user = self.get_user()
        if not self.user:
            messages.error(request, "El enlace de restablecimiento es inválido o ha expirado.")
            return redirect("accounts:password_reset_request")
        return super().dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        """
        Pasa el usuario al formulario.
        """
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.user, **self.get_form_kwargs())
    
    def form_valid(self, form):
        """
        Guarda la nueva contraseña y muestra mensaje de éxito.
        """
        form.save()
        messages.success(
            self.request, 
            "Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña."
        )
        return super().form_valid(form)


class PasswordResetCompleteView(TemplateView):
    """
    Vista de confirmación después de completar el restablecimiento.
    """
    
    template_name = "accounts/password/password_reset_complete.html"
