from django.urls import path
from dashboard.views import UserListView, UserDetailView, UserEditView, UserDeleteView

urlpatterns = [
    path("usuarios/", UserListView.as_view(), name="user_list"),
    path("usuarios/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("usuarios/<int:pk>/editar/", UserEditView.as_view(), name="user_edit"),
    path("usuarios/<int:pk>/eliminar/",
         UserDeleteView.as_view(), name="user_delete"),
]
