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
    # Survey management views
    survey_list,
    survey_create,
    survey_detail,
    survey_update,
    survey_delete,
    survey_duplicate,
    survey_questions,
    question_options,
    survey_results,
    survey_export,
    send_surveys,
)
from .views import (
    # Program management views
    ProgramListView,
    ProgramDetailView,
    ProgramCreateView,
    ProgramUpdateView,
    ProgramDeleteView,
    # Module management views
    ModuleListView,
    ModuleDetailView,
    ModuleCreateView,
    ModuleUpdateView,
    ModuleDeleteView,
    # Session management views
    SessionListView,
    SessionDetailView,
    SessionCreateView,
    SessionUpdateView,
    SessionDeleteView,
    # Material management views
    MaterialCreateView,
    MaterialUpdateView,
    MaterialDeleteView,
    # Assignment management views (Manager only)
    AssignmentListView,
    AssignmentCreateView,
    AssignmentDetailView,
    AssignmentUpdateView,
    AssignmentDeleteView,
    # Final feedback management views
    FinalFeedbackListView,
    FinalFeedbackDetailView,
    FinalFeedbackCreateView,
    FinalFeedbackUpdateView,
    FinalFeedbackDeleteView,
    FinalFeedbackDuplicateView,
    # Feedback question management views
    FeedbackQuestionCreateView,
    FeedbackQuestionUpdateView,
    FeedbackQuestionDeleteView,
)
from .views import delete_program_comment
from .views import SessionCommentModerationView
from .views import SessionCommentReplyView
from .views import ProgramCommentDeleteView

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

    # Survey management URLs
    path("encuestas/", survey_list, name="survey_list"),
    path("encuestas/crear/", survey_create, name="survey_create"),
    path("encuestas/<int:pk>/", survey_detail, name="survey_detail"),
    path("encuestas/<int:pk>/editar/", survey_update, name="survey_update"),
    path("encuestas/<int:pk>/eliminar/", survey_delete, name="survey_delete"),
    path("encuestas/<int:pk>/duplicar/",
         survey_duplicate, name="survey_duplicate"),
    path("encuestas/<int:pk>/preguntas/",
         survey_questions, name="survey_questions"),
    path("preguntas/<int:question_pk>/opciones/",
         question_options, name="question_options"),
    path("encuestas/<int:pk>/resultados/",
         survey_results, name="survey_results"),
    path("encuestas/<int:pk>/exportar/",
         survey_export, name="survey_export"),
    path("eventos/<int:event_pk>/enviar-encuestas/",
         send_surveys, name="send_surveys"),

    # Program management URLs
    path("programas/", ProgramListView.as_view(), name="program_list"),
    path("programas/crear/", ProgramCreateView.as_view(), name="program_create"),
    path("programas/<int:pk>/", ProgramDetailView.as_view(), name="program_detail"),
    path("programas/<int:pk>/editar/",
         ProgramUpdateView.as_view(), name="program_update"),
    path("programas/<int:pk>/eliminar/",
         ProgramDeleteView.as_view(), name="program_delete"),

    # Module management URLs
    path("programas/<int:program_pk>/modulos/",
         ModuleListView.as_view(), name="module_list"),
    path("programas/<int:program_pk>/modulos/crear/",
         ModuleCreateView.as_view(), name="module_create"),
    path("programas/<int:program_pk>/modulos/<int:pk>/",
         ModuleDetailView.as_view(), name="module_detail"),
    path("programas/<int:program_pk>/modulos/<int:pk>/editar/",
         ModuleUpdateView.as_view(), name="module_update"),
    path("programas/<int:program_pk>/modulos/<int:pk>/eliminar/",
         ModuleDeleteView.as_view(), name="module_delete"),

    # Session management URLs
    path("modulos/<int:module_pk>/sesiones/",
         SessionListView.as_view(), name="session_list"),
    path("modulos/<int:module_pk>/sesiones/crear/",
         SessionCreateView.as_view(), name="session_create"),
    path("modulos/<int:module_pk>/sesiones/<int:pk>/",
         SessionDetailView.as_view(), name="session_detail"),
    path("modulos/<int:module_pk>/sesiones/<int:pk>/editar/",
         SessionUpdateView.as_view(), name="session_update"),
    path("modulos/<int:module_pk>/sesiones/<int:pk>/eliminar/",
         SessionDeleteView.as_view(), name="session_delete"),

    # Material management URLs
    path("sesiones/<int:session_pk>/materiales/crear/",
         MaterialCreateView.as_view(), name="material_create"),
    path("sesiones/<int:session_pk>/materiales/<int:pk>/editar/",
         MaterialUpdateView.as_view(), name="material_update"),
    path("sesiones/<int:session_pk>/materiales/<int:pk>/eliminar/",
         MaterialDeleteView.as_view(), name="material_delete"),

    # Assignment management URLs (Manager only)
    path("asignaciones/", AssignmentListView.as_view(), name="assignment_list"),
    path("asignaciones/crear/", AssignmentCreateView.as_view(),
         name="assignment_create"),
    path("asignaciones/<int:pk>/", AssignmentDetailView.as_view(),
         name="assignment_detail"),
    path("asignaciones/<int:pk>/editar/",
         AssignmentUpdateView.as_view(), name="assignment_update"),
    path("asignaciones/<int:pk>/eliminar/",
         AssignmentDeleteView.as_view(), name="assignment_delete"),

    # Final feedback management URLs
    path("evaluaciones-finales/", FinalFeedbackListView.as_view(),
         name="final_feedback_list"),
    path("evaluaciones-finales/crear/",
         FinalFeedbackCreateView.as_view(), name="final_feedback_create"),
    path("evaluaciones-finales/<int:pk>/",
         FinalFeedbackDetailView.as_view(), name="final_feedback_detail"),
    path("evaluaciones-finales/<int:pk>/editar/",
         FinalFeedbackUpdateView.as_view(), name="final_feedback_update"),
    path("evaluaciones-finales/<int:pk>/eliminar/",
         FinalFeedbackDeleteView.as_view(), name="final_feedback_delete"),
    path("evaluaciones-finales/<int:pk>/duplicar/",
         FinalFeedbackDuplicateView.as_view(), name="final_feedback_duplicate"),

    # Feedback question management URLs
    path("evaluaciones-finales/<int:feedback_pk>/preguntas/crear/",
         FeedbackQuestionCreateView.as_view(), name="feedback_question_create"),
    path("evaluaciones-finales/<int:feedback_pk>/preguntas/<int:pk>/editar/",
         FeedbackQuestionUpdateView.as_view(), name="feedback_question_update"),
    path("evaluaciones-finales/<int:feedback_pk>/preguntas/<int:pk>/eliminar/",
         FeedbackQuestionDeleteView.as_view(), name="feedback_question_delete"),
]

urlpatterns += [
    path('comentarios-programa/<int:pk>/eliminar/',
         ProgramCommentDeleteView.as_view(), name='program_comment_delete'),
    path('programs/<int:program_pk>/modules/<int:module_pk>/sessions/<int:session_pk>/comments/',
         SessionCommentModerationView.as_view(), name='session_comment_moderation'),
    path('programs/<int:program_pk>/modules/<int:module_pk>/sessions/<int:session_pk>/comments/<int:parent_comment_id>/reply/',
         SessionCommentReplyView.as_view(), name='session_comment_reply'),
]
