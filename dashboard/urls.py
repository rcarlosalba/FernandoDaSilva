"""
URL configuration for dashboard app.
"""
from django.urls import path, include
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
from events.views import (
    # Event management views
    event_list,
    event_create,
    event_detail,
    event_update,
    event_delete,
    # Event category management views
    category_list,
    category_create,
    category_detail,
    category_update,
    category_delete,
    # Payment method management views
    payment_method_list,
    payment_method_create,
    payment_method_detail,
    payment_method_update,
    payment_method_delete,
    # Registration management views
    registration_list,
    registration_detail,
    registration_approve,
    registration_reject,
    # Payment management views
    payment_verify,
    # Statistics views
    event_statistics,
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

    # Newsletter management URLs
    path("newsletter/", include("newsletter.urls")),

    # Events management URLs
    path("eventos/", event_list, name="event_list"),
    path("eventos/crear/", event_create, name="event_create"),
    path("eventos/<int:pk>/", event_detail, name="event_detail"),
    path("eventos/<int:pk>/editar/", event_update, name="event_update"),
    path("eventos/<int:pk>/eliminar/", event_delete, name="event_delete"),

    # Event categories management URLs
    path("categorias-eventos/", category_list, name="event_category_list"),
    path("categorias-eventos/crear/",
         category_create, name="event_category_create"),
    path("categorias-eventos/<int:pk>/",
         category_detail, name="event_category_detail"),
    path("categorias-eventos/<int:pk>/editar/",
         category_update, name="event_category_update"),
    path("categorias-eventos/<int:pk>/eliminar/",
         category_delete, name="event_category_delete"),

    # Payment methods management URLs
    path("metodos-pago/", payment_method_list, name="payment_method_list"),
    path("metodos-pago/crear/", payment_method_create,
         name="payment_method_create"),
    path("metodos-pago/<int:pk>/", payment_method_detail,
         name="payment_method_detail"),
    path("metodos-pago/<int:pk>/editar/",
         payment_method_update, name="payment_method_update"),
    path("metodos-pago/<int:pk>/eliminar/",
         payment_method_delete, name="payment_method_delete"),

    # Registrations management URLs
    path("inscripciones/", registration_list, name="registration_list"),
    path("inscripciones/<int:pk>/", registration_detail,
         name="registration_detail"),
    path("inscripciones/<int:pk>/aprobar/",
         registration_approve, name="registration_approve"),
    path("inscripciones/<int:pk>/rechazar/",
         registration_reject, name="registration_reject"),

    # Payments management URLs
    path("pagos/<int:pk>/verificar/", payment_verify, name="payment_verify"),

    # Events statistics URLs
    path("estadisticas-eventos/", event_statistics, name="statistics"),
]
