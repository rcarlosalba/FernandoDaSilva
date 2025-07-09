"""
URL configuration for dashboard app.
"""
from django.urls import path
from .views import (
    DashboardIndexView,
    UserListView,
    UserDetailView,
    UserEditView,
    UserDeleteView,
    # Blog management views
    BlogPostListView,
    BlogPostDetailView,
    BlogPostCreateView,
    BlogPostUpdateView,
    BlogPostDeleteView,
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    TagListView,
    TagDetailView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
    CommentModerationView,
    CommentApproveView,
    CommentRejectView,
    CommentDeleteView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardIndexView.as_view(), name="index"),
    path("usuarios/", UserListView.as_view(), name="user_list"),
    path("usuarios/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("usuarios/<int:pk>/editar/", UserEditView.as_view(), name="user_edit"),
    path("usuarios/<int:pk>/eliminar/",
         UserDeleteView.as_view(), name="user_delete"),

    # Blog management URLs
    path("blog/", BlogPostListView.as_view(), name="blog_post_list"),
    path("blog/<int:pk>/", BlogPostDetailView.as_view(), name="blog_post_detail"),
    path("blog/crear/", BlogPostCreateView.as_view(), name="blog_post_create"),
    path("blog/<int:pk>/editar/", BlogPostUpdateView.as_view(),
         name="blog_post_update"),
    path("blog/<int:pk>/eliminar/",
         BlogPostDeleteView.as_view(), name="blog_post_delete"),

    # Category management URLs
    path("categorias/", CategoryListView.as_view(), name="category_list"),
    path("categorias/crear/", CategoryCreateView.as_view(), name="category_create"),
    path("categorias/<int:pk>/", CategoryDetailView.as_view(),
         name="category_detail"),
    path("categorias/<int:pk>/editar/",
         CategoryUpdateView.as_view(), name="category_update"),
    path("categorias/<int:pk>/eliminar/",
         CategoryDeleteView.as_view(), name="category_delete"),

    # Tag management URLs
    path("etiquetas/", TagListView.as_view(), name="tag_list"),
    path("etiquetas/crear/", TagCreateView.as_view(), name="tag_create"),
    path("etiquetas/<int:pk>/", TagDetailView.as_view(), name="tag_detail"),
    path("etiquetas/<int:pk>/editar/",
         TagUpdateView.as_view(), name="tag_update"),
    path("etiquetas/<int:pk>/eliminar/",
         TagDeleteView.as_view(), name="tag_delete"),

    # Comment moderation URLs
    path("comentarios/", CommentModerationView.as_view(),
         name="comment_moderation"),
    path("comentarios/<int:pk>/aprobar/",
         CommentApproveView.as_view(), name="comment_approve"),
    path("comentarios/<int:pk>/rechazar/",
         CommentRejectView.as_view(), name="comment_reject"),
    path("comentarios/<int:pk>/eliminar/",
         CommentDeleteView.as_view(), name="comment_delete"),
]
