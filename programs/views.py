from django.shortcuts import render, get_object_or_404
from constants.constant import student_assigned_to_program_required
from programs.models import Program, Assignment, Session, Module


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
    # Se pueden añadir materiales y comentarios en el futuro
    return render(request, 'programs/session_detail.html', {'session': session})
