from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import CustomPasswordChangeForm
from .views import (
    AccountDeleteView,
    CompleteProfileView,
    CustomLoginView,
    CustomLogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PasswordResetSentView,
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
    # Password Reset - Custom Implementation
    path(
        "restablecer-contrasena/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "restablecer-contrasena/enviado/",
        PasswordResetSentView.as_view(),
        name="password_reset_sent",
    ),
    path(
        "restablecer-contrasena/confirmar/<str:signed_user_id>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "restablecer-contrasena/completo/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
