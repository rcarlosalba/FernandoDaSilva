from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.template.loader import render_to_string
from constants.constant import student_assigned_to_program_required
from programs.models import Program, Assignment, Session, Module, SessionCompletion, FinalFeedback, FeedbackQuestion, FeedbackResponse
from .forms import CommentForm
from .models import Session, Comment
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def index(request):
    """
    Vista del dashboard personal del estudiante con sus programas asignados.
    """
    from programs.models import Assignment
    assignments = Assignment.objects.select_related(
        'program').filter(student=request.user, status__in=['active', 'completed', 'Activo']).order_by('-assigned_at')
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


@require_POST
@student_assigned_to_program_required
def complete_session(request, sesion_pk):
    """
    Marca una sesión como completada para el estudiante actual.
    Devuelve el nuevo porcentaje de progreso y, si corresponde, el mensaje de felicitación del módulo.
    """
    user = request.user
    session = get_object_or_404(Session, pk=sesion_pk)
    program = session.module.program
    # Buscar la asignación activa
    try:
        assignment = Assignment.objects.get(
            student=user, program=program, status__in=["active", "Activo"])
    except Assignment.DoesNotExist:
        return JsonResponse({"success": False, "error": "No tienes asignación activa para este programa."}, status=403)

    # Verificar si ya está completada
    already_completed = SessionCompletion.objects.filter(
        assignment=assignment, session=session).exists()
    if already_completed:
        assignment.update_progress()
        return JsonResponse({
            "success": True,
            "progress": assignment.progress_percentage,
            "congratulation": None
        })

    # Marcar como completada
    SessionCompletion.objects.create(assignment=assignment, session=session)
    assignment.update_progress()

    # Verificar si todas las sesiones del módulo están completadas
    module_sessions = session.module.sessions.all()
    completed_sessions = SessionCompletion.objects.filter(
        assignment=assignment,
        session__in=module_sessions
    ).count()
    all_completed = completed_sessions == module_sessions.count()
    congratulation = session.module.congratulation_message if all_completed and session.module.congratulation_message else None

    return JsonResponse({
        "success": True,
        "progress": assignment.progress_percentage,
        "congratulation": congratulation
    })


@student_assigned_to_program_required
@require_http_methods(["GET", "POST"])
def final_feedback(request, programa_pk):
    """
    Permite al estudiante responder la Evaluación Final de su programa asignado, solo si tiene progreso 100%.
    """
    user = request.user
    program = get_object_or_404(Program, pk=programa_pk)
    try:
        assignment = Assignment.objects.get(student=user, program=program, status__in=[
                                            "active", "completed", "Activo"])
    except Assignment.DoesNotExist:
        return render(request, 'programs/final_feedback_form.html', {
            'error': 'No tienes una asignación activa para este programa.'
        })

    if assignment.progress_percentage < 100:
        return render(request, 'programs/final_feedback_form.html', {
            'error': 'Debes completar el programa antes de acceder a la evaluación final.'
        })

    # Verificar si existe evaluación final
    try:
        feedback = program.final_feedback
    except FinalFeedback.DoesNotExist:
        return render(request, 'programs/final_feedback_form.html', {
            'error': 'No hay una evaluación final disponible para este programa.'
        })

    # Verificar si ya respondió
    already_responded = FeedbackResponse.objects.filter(
        assignment=assignment, question__final_feedback=feedback).exists()
    if already_responded:
        return render(request, 'programs/final_feedback_form.html', {
            'feedback': feedback,
            'already_responded': True
        })

    # Obtener preguntas
    questions = feedback.questions.order_by('order')

    if request.method == 'POST':
        responses = []
        for question in questions:
            answer = request.POST.get(f'question_{question.id}', '').strip()
            if question.required and not answer:
                return render(request, 'programs/final_feedback_form.html', {
                    'feedback': feedback,
                    'questions': questions,
                    'error': f'La pregunta "{question.question}" es obligatoria.'
                })
            if answer:
                responses.append(FeedbackResponse(
                    assignment=assignment,
                    question=question,
                    response=answer
                ))
        # Guardar respuestas
        FeedbackResponse.objects.bulk_create(responses)
        return render(request, 'programs/final_feedback_form.html', {
            'feedback': feedback,
            'success': '¡Gracias por tu feedback!'
        })

    return render(request, 'programs/final_feedback_form.html', {
        'feedback': feedback,
        'questions': questions
    })
