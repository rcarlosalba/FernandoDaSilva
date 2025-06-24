from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView
)
from django.core.signing import BadSignature, SignatureExpired, Signer
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView

from constants.constant import UserRoles
from .forms import (
    CompleteProfileForm,
    LoginForm,
    ProfileEditForm,
    SubscriberRegistrationForm,
)
from .utils import send_welcome_subscriber_email, send_welcome_member_email, send_account_deactivation_email
from .models import Profile, User

# TODO: Implement email sending for registration and password reset.


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
