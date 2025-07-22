from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import CustomPasswordChangeForm
from .views import (
    AccountDeleteView,
    CompleteProfileView,
    CustomLoginView,
    CustomLogoutView,
    ProfileEditView,
    ProfileView,
    RegistrationDoneView,
    SubscriberRegistrationView,
)

app_name = "accounts"

urlpatterns = [
    # Registration
    path(
        "registro/",
        SubscriberRegistrationView.as_view(),
        name="register_subscriber",
    ),
    path(
        "registro/completo/",
        RegistrationDoneView.as_view(),
        name="registration_done",
    ),
    path(
        "registro/completar-perfil/<str:signed_user_id>/",
        CompleteProfileView.as_view(),
        name="complete_profile",
    ),
    # Authentication
    path("iniciar-sesion/", CustomLoginView.as_view(), name="login"),
    path(
        "cerrar-sesion/",
        CustomLogoutView.as_view(),
        name="logout",
    ),
    # Profile Management
    path("perfil/", ProfileView.as_view(), name="profile"),
    path("perfil/editar/", ProfileEditView.as_view(), name="profile_edit"),
    path("perfil/eliminar/", AccountDeleteView.as_view(), name="account_delete"),
    # Password Change
    path(
        "perfil/cambiar-contrasena/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password/password_change_form.html",
            form_class=CustomPasswordChangeForm,
            success_url="/cuentas/perfil/cambiar-contrasena/hecho/",
        ),
        name="password_change",
    ),
    path(
        "perfil/cambiar-contrasena/hecho/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # Password Reset
    path(
        "restablecer-contrasena/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password/password_reset_form.html",
            email_template_name="accounts/email/password_reset_email.html",
            subject_template_name="accounts/email/password_reset_subject.txt",
            success_url="/cuentas/restablecer-contrasena/enviado/",
        ),
        name="password_reset",
    ),
    path(
        "restablecer-contrasena/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "restablecer-contrasena/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password/password_reset_confirm.html",
            success_url="/cuentas/restablecer-contrasena/completo/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "restablecer-contrasena/completo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
