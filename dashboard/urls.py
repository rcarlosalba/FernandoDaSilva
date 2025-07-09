from django.urls import path
from .views import (
    DashboardIndexView,
    UserListView,
    UserDetailView,
    UserEditView,
    UserDeleteView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardIndexView.as_view(), name="index"),
    path("usuarios/", UserListView.as_view(), name="user_list"),
    path("usuarios/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("usuarios/<int:pk>/editar/", UserEditView.as_view(), name="user_edit"),
    path("usuarios/<int:pk>/eliminar/", UserDeleteView.as_view(), name="user_delete"),
]