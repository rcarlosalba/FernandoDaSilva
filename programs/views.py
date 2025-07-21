from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.template.loader import render_to_string
from constants.constant import student_assigned_to_program_required
from django.contrib import messages
from programs.models import Program, Assignment, Session, Module
from .forms import CommentForm
from .models import Session, Comment


def index(request):
    """
    Vista del dashboard personal del estudiante con sus programas asignados.
    """
    from programs.models import Assignment
    assignments = Assignment.objects.select_related(
        'program').filter(student=request.user, status='active')
    program_assignments = [
        {
            'program': assignment.program,
            'assignment': assignment
        }
        for assignment in assignments
    ]
    return render(request, 'programs/index.html', {'program_assignments': program_assignments})


@student_assigned_to_program_required
def program_detail(request, programa_pk):
    """
    Vista del detalle de un programa y sus módulos para el estudiante.
    """
    program = get_object_or_404(Program, pk=programa_pk)
    modules = Module.objects.filter(program=program).order_by('order')
    return render(request, 'programs/program_detail.html', {'program': program, 'modules': modules})


@student_assigned_to_program_required
def session_detail(request, sesion_pk):
    """
    Vista del detalle de una sesión (lección) para el estudiante.
    """
    session = get_object_or_404(Session, pk=sesion_pk)
    user = request.user
    # Flags de permisos
    can_comment = False
    can_reply = False
    can_delete = False
    if user.is_authenticated:
        if user.role == 'student':
            can_comment = Assignment.objects.filter(
                student=user, program=session.module.program, status__in=['active', 'Activo']).exists()
            can_reply = can_comment
        if user.role == 'manager':
            can_delete = True
    root_comments = session.comments.filter(parent__isnull=True)
    return render(request, 'programs/session_detail.html', {
        'session': session,
        'can_comment': can_comment,
        'can_reply': can_reply,
        'can_delete': can_delete,
        'user': user,
        'root_comments': root_comments,
    })


@require_POST
@student_assigned_to_program_required
def add_session_comment(request, sesion_pk):
    session = Session.objects.get(pk=sesion_pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.session = session
        comment.author = request.user
        comment.save()
        messages.success(request, "Comentario publicado correctamente.")
        # Para AJAX: renderizar el comentario como HTML
        html = render_to_string(
            'programs/components/comment.html',
            {
                'comment': comment,
                'user': request.user,
                'can_delete': False,  # Solo managers pueden eliminar
                'can_reply': True,    # El estudiante puede responder
            },
            request=request
        )
        return JsonResponse({'success': True, 'html': html})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
