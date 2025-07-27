from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Max
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.views import View
from django.urls import reverse_lazy, reverse
from constants.constant import manager_required_class, manager_required
from dashboard.forms import (
    ProgramForm, ModuleForm, SessionForm, MaterialForm,
    AssignmentForm, FinalFeedbackForm, FeedbackQuestionForm
)
from programs.models import (
    Program, Module, Session, Material, Assignment,
    FinalFeedback, FeedbackQuestion, FeedbackResponse, Comment
)

# Program Management Views


@manager_required_class
class ProgramListView(ListView):
    """List all programs for management."""
    model = Program
    template_name = 'dashboard/programs/program_list.html'
    context_object_name = 'programs'
    paginate_by = 20

    def get_queryset(self):
        # Prefetch módulos y sesiones para eficiencia
        return Program.objects.prefetch_related('modules__sessions').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Totales
        context['total_programs'] = Program.objects.count()
        context['total_modules'] = Module.objects.count()
        context['total_sessions'] = Session.objects.count()
        context['total_materials'] = Material.objects.count()
        context['total_assignments'] = Assignment.objects.count()
        context['total_feedbacks'] = FinalFeedback.objects.count()
        context['total_questions'] = FeedbackQuestion.objects.count()
        context['total_comments'] = Comment.objects.count()
        # Actividad reciente
        context['recent_programs'] = Program.objects.order_by(
            '-created_at')[:5]
        context['recent_assignments'] = Assignment.objects.select_related(
            'student', 'program').order_by('-assigned_at')[:5]
        context['recent_comments'] = Comment.objects.select_related(
            'author', 'session').order_by('-created_at')[:5]
        return context


@manager_required_class
class ProgramDetailView(DetailView):
    """View detailed information about a specific program."""
    model = Program
    template_name = 'dashboard/programs/program_detail.html'
    context_object_name = 'program'

    def get_queryset(self):
        return Program.objects.prefetch_related('modules__sessions').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.prefetch_related(
            'sessions').order_by('order')
        context['total_sessions'] = sum(
            module.sessions.count() for module in self.object.modules.all())
        context['assignments_count'] = self.object.assignments.count()
        return context


@manager_required_class
class ProgramCreateView(CreateView):
    """Create a new program."""
    model = Program
    template_name = 'dashboard/programs/program_form.html'
    form_class = ProgramForm

    def form_valid(self, form):
        messages.success(self.request, 'Programa creado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:program_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class ProgramUpdateView(UpdateView):
    """Update an existing program."""
    model = Program
    template_name = 'dashboard/programs/program_form.html'
    form_class = ProgramForm

    def form_valid(self, form):
        messages.success(self.request, 'Programa actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:program_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class ProgramDeleteView(DeleteView):
    """Delete a program."""
    model = Program
    success_url = reverse_lazy('dashboard:program_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = self.object.title
        self.object.delete()
        messages.success(
            request, f'Programa "{title}" eliminado exitosamente.')
        return redirect(self.success_url)

# Module Management Views


@manager_required_class
class ModuleListView(ListView):
    """List all modules for a specific program."""
    model = Module
    template_name = 'dashboard/programs/module_list.html'
    context_object_name = 'modules'
    paginate_by = 20

    def get_queryset(self):
        self.program = get_object_or_404(Program, pk=self.kwargs['program_pk'])
        return Module.objects.filter(program=self.program).prefetch_related('sessions').order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = self.program
        context['total_sessions'] = sum(
            module.sessions.count() for module in self.object_list)
        return context


@manager_required_class
class ModuleDetailView(DetailView):
    """View detailed information about a specific module."""
    model = Module
    template_name = 'dashboard/programs/module_detail.html'
    context_object_name = 'module'

    def get_queryset(self):
        return Module.objects.filter(program_id=self.kwargs['program_pk']).prefetch_related('sessions__materials')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = self.object.program
        context['sessions'] = self.object.sessions.prefetch_related(
            'materials').order_by('order')
        context['total_materials'] = sum(
            session.materials.count() for session in self.object.sessions.all())
        return context


@manager_required_class
class ModuleCreateView(CreateView):
    """Create a new module."""
    model = Module
    template_name = 'dashboard/programs/module_form.html'
    form_class = ModuleForm

    def form_valid(self, form):
        form.instance.program_id = self.kwargs['program_pk']
        messages.success(self.request, 'Módulo creado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:module_detail', kwargs={
            'program_pk': self.kwargs['program_pk'],
            'pk': self.object.pk
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = get_object_or_404(
            Program, pk=self.kwargs['program_pk'])
        return context


@manager_required_class
class ModuleUpdateView(UpdateView):
    """Update an existing module."""
    model = Module
    template_name = 'dashboard/programs/module_form.html'
    form_class = ModuleForm

    def get_queryset(self):
        return Module.objects.filter(program_id=self.kwargs['program_pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Módulo actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:module_detail', kwargs={
            'program_pk': self.kwargs['program_pk'],
            'pk': self.object.pk
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program'] = self.object.program
        return context


@manager_required_class
class ModuleDeleteView(DeleteView):
    """Delete a module."""
    model = Module
    success_url = reverse_lazy('dashboard:program_list')

    def get_queryset(self):
        return Module.objects.filter(program_id=self.kwargs['program_pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = self.object.title
        program_pk = self.object.program.pk
        self.object.delete()
        messages.success(request, f'Módulo "{title}" eliminado exitosamente.')
        return redirect('dashboard:program_detail', pk=program_pk)

# Session Management Views


@manager_required_class
class SessionListView(ListView):
    """List all sessions for a specific module."""
    model = Session
    template_name = 'dashboard/programs/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        self.module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
        return Session.objects.filter(module=self.module).prefetch_related('materials').order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.module
        context['program'] = self.module.program
        context['total_materials'] = sum(
            session.materials.count() for session in self.object_list)
        return context


@manager_required_class
class SessionDetailView(DetailView):
    """View detailed information about a specific session."""
    model = Session
    template_name = 'dashboard/programs/session_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return Session.objects.filter(module_id=self.kwargs['module_pk']).prefetch_related('materials')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.object.module
        context['program'] = self.object.module.program
        context['materials'] = self.object.materials.order_by('created_at')
        return context


@manager_required_class
class SessionCreateView(CreateView):
    """Create a new session."""
    model = Session
    template_name = 'dashboard/programs/session_form.html'
    form_class = SessionForm

    def form_valid(self, form):
        form.instance.module_id = self.kwargs['module_pk']
        messages.success(self.request, 'Sesión creada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:session_detail', kwargs={
            'module_pk': self.kwargs['module_pk'],
            'pk': self.object.pk
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = get_object_or_404(
            Module, pk=self.kwargs['module_pk'])
        context['program'] = context['module'].program
        return context


@manager_required_class
class SessionUpdateView(UpdateView):
    """Update an existing session."""
    model = Session
    template_name = 'dashboard/programs/session_form.html'
    form_class = SessionForm

    def get_queryset(self):
        return Session.objects.filter(module_id=self.kwargs['module_pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Sesión actualizada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:session_detail', kwargs={
            'module_pk': self.kwargs['module_pk'],
            'pk': self.object.pk
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.object.module
        context['program'] = self.object.module.program
        return context


@manager_required_class
class SessionDeleteView(DeleteView):
    """Delete a session."""
    model = Session
    success_url = reverse_lazy('dashboard:program_list')

    def get_queryset(self):
        return Session.objects.filter(module_id=self.kwargs['module_pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = self.object.title
        module_pk = self.object.module.pk
        self.object.delete()
        messages.success(request, f'Sesión "{title}" eliminada exitosamente.')
        return redirect('dashboard:module_detail', program_pk=module_pk, pk=module_pk)

# Material Management Views


@manager_required_class
class MaterialCreateView(CreateView):
    """Create a new material."""
    model = Material
    template_name = 'dashboard/programs/material_form.html'
    form_class = MaterialForm

    def form_valid(self, form):
        form.instance.session_id = self.kwargs['session_pk']
        messages.success(self.request, 'Material creado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:session_detail', kwargs={
            'module_pk': self.object.session.module.pk,
            'pk': self.object.session.pk
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = get_object_or_404(
            Session, pk=self.kwargs['session_pk'])
        context['module'] = context['session'].module
        context['program'] = context['session'].module.program
        return context


@manager_required_class
class MaterialUpdateView(UpdateView):
    """Update an existing material."""
    model = Material
    template_name = 'dashboard/programs/material_form.html'
    form_class = MaterialForm

    def get_queryset(self):
        return Material.objects.filter(session_id=self.kwargs['session_pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Material actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:session_detail', kwargs={
            'module_pk': self.object.session.module.pk,
            'pk': self.object.session.pk
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = self.object.session
        context['module'] = self.object.session.module
        context['program'] = self.object.session.module.program
        return context


@manager_required_class
class MaterialDeleteView(DeleteView):
    """Delete a material."""
    model = Material
    success_url = reverse_lazy('dashboard:program_list')

    def get_queryset(self):
        return Material.objects.filter(session_id=self.kwargs['session_pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = self.object.title
        session_pk = self.object.session.pk
        module_pk = self.object.session.module.pk
        self.object.delete()
        messages.success(
            request, f'Material "{title}" eliminado exitosamente.')
        return redirect('dashboard:session_detail', module_pk=module_pk, pk=session_pk)

# Assignment Management Views


@manager_required_class
class AssignmentListView(ListView):
    """List all assignments for management."""
    model = Assignment
    template_name = 'dashboard/programs/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 20

    def get_queryset(self):
        return Assignment.objects.select_related('student', 'program').order_by('-assigned_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_assignments'] = Assignment.objects.count()
        context['active_assignments'] = Assignment.objects.filter(
            status='active').count()
        context['completed_assignments'] = Assignment.objects.filter(
            status='completed').count()
        return context


@manager_required_class
class AssignmentDetailView(DetailView):
    """View detailed information about a specific assignment."""
    model = Assignment
    template_name = 'dashboard/programs/assignment_detail.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.select_related('student', 'program').prefetch_related('completed_sessions__session')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_sessions'] = self.object.completed_sessions.select_related(
            'session__module').order_by('session__module__order', 'session__order')
        context['total_sessions'] = self.object.program.total_sessions
        return context


@manager_required_class
class AssignmentCreateView(CreateView):
    """Create a new assignment."""
    model = Assignment
    template_name = 'dashboard/programs/assignment_form.html'
    form_class = AssignmentForm

    def form_valid(self, form):
        student = form.cleaned_data['student']
        from constants.constant import UserRoles
        if student.role != UserRoles.STUDENT:
            student.role = UserRoles.STUDENT
            student.save()
        response = super().form_valid(form)
        # Enviar correo de bienvenida
        from programs.utils import send_welcome_assignment_email
        email_sent = send_welcome_assignment_email(
            self.object, manager_email=self.request.user.email)
        if not email_sent:
            messages.warning(
                self.request, 'La asignación fue creada, pero hubo un error al enviar el correo de bienvenida al estudiante.')
        else:
            messages.success(self.request, 'Asignación creada exitosamente.')
        return response

    def get_success_url(self):
        return reverse_lazy('dashboard:assignment_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class AssignmentUpdateView(UpdateView):
    """Update an existing assignment."""
    model = Assignment
    template_name = 'dashboard/programs/assignment_form.html'
    form_class = AssignmentForm

    def form_valid(self, form):
        messages.success(self.request, 'Asignación actualizada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:assignment_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class AssignmentDeleteView(DeleteView):
    """Delete an assignment."""
    model = Assignment
    success_url = reverse_lazy('dashboard:assignment_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        student_name = self.object.student.get_full_name()
        program_title = self.object.program.title
        self.object.delete()
        messages.success(
            request, f'Asignación de {student_name} al programa "{program_title}" eliminada exitosamente.')
        return redirect(self.success_url)

# Final Feedback Management Views


@manager_required_class
class FinalFeedbackListView(ListView):
    """List all final feedback forms for management."""
    model = FinalFeedback
    template_name = 'dashboard/programs/final_feedback_list.html'
    context_object_name = 'final_feedbacks'
    paginate_by = 20

    def get_queryset(self):
        return FinalFeedback.objects.select_related('program').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_feedbacks'] = FinalFeedback.objects.count()
        context['total_questions'] = FeedbackQuestion.objects.count()
        context['total_responses'] = FeedbackResponse.objects.count()
        return context


@manager_required_class
class FinalFeedbackDetailView(DetailView):
    """View detailed information about a specific final feedback form."""
    model = FinalFeedback
    template_name = 'dashboard/programs/final_feedback_detail.html'
    context_object_name = 'feedback'

    def get_queryset(self):
        return FinalFeedback.objects.select_related('program').prefetch_related('questions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.order_by('order')
        context['total_responses'] = FeedbackResponse.objects.filter(
            question__final_feedback=self.object).count()
        return context


@manager_required_class
class FinalFeedbackCreateView(CreateView):
    """Create a new final feedback form."""
    model = FinalFeedback
    template_name = 'dashboard/programs/final_feedback_form.html'
    form_class = FinalFeedbackForm

    def form_valid(self, form):
        messages.success(self.request, 'Evaluación final creada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:final_feedback_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class FinalFeedbackUpdateView(UpdateView):
    """Update an existing final feedback form."""
    model = FinalFeedback
    template_name = 'dashboard/programs/final_feedback_form.html'
    form_class = FinalFeedbackForm

    def form_valid(self, form):
        messages.success(
            self.request, 'Evaluación final actualizada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:final_feedback_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class FinalFeedbackDeleteView(DeleteView):
    """Delete a final feedback form."""
    model = FinalFeedback
    success_url = reverse_lazy('dashboard:final_feedback_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = self.object.title
        self.object.delete()
        messages.success(
            request, f'Evaluación final "{title}" eliminada exitosamente.')
        return redirect(self.success_url)


@manager_required_class
class FinalFeedbackDuplicateView(View):
    """Duplicate a final feedback form."""

    def get(self, request, pk):
        original_feedback = get_object_or_404(FinalFeedback, pk=pk)
        new_feedback = FinalFeedback.objects.create(
            program=original_feedback.program,
            title=f"{original_feedback.title} (Copia)",
            description=original_feedback.description
        )
        for question in original_feedback.questions.all():
            FeedbackQuestion.objects.create(
                final_feedback=new_feedback,
                question=question.question,
                type=question.type,
                required=question.required,
                order=question.order
            )
        messages.success(
            request, f'Evaluación final "{original_feedback.title}" duplicada exitosamente.')
        return redirect('dashboard:final_feedback_detail', pk=new_feedback.pk)

# Feedback Question Management Views


@manager_required_class
class FeedbackQuestionCreateView(CreateView):
    """Create a new feedback question."""
    model = FeedbackQuestion
    template_name = 'dashboard/programs/feedback_question_form.html'
    form_class = FeedbackQuestionForm

    def form_valid(self, form):
        form.instance.final_feedback_id = self.kwargs['feedback_pk']
        max_order = FeedbackQuestion.objects.filter(
            final_feedback_id=self.kwargs['feedback_pk']).aggregate(
            max_order=Max('order'))['max_order'] or 0
        form.instance.order = max_order + 1
        messages.success(self.request, 'Pregunta creada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:final_feedback_detail', kwargs={'pk': self.kwargs['feedback_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback'] = get_object_or_404(
            FinalFeedback, pk=self.kwargs['feedback_pk'])
        return context


@manager_required_class
class FeedbackQuestionUpdateView(UpdateView):
    """Update an existing feedback question."""
    model = FeedbackQuestion
    template_name = 'dashboard/programs/feedback_question_form.html'
    form_class = FeedbackQuestionForm

    def get_queryset(self):
        return FeedbackQuestion.objects.filter(final_feedback_id=self.kwargs['feedback_pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Pregunta actualizada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:final_feedback_detail', kwargs={'pk': self.kwargs['feedback_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback'] = self.object.final_feedback
        return context


@manager_required_class
class FeedbackQuestionDeleteView(DeleteView):
    """Delete a feedback question."""
    model = FeedbackQuestion
    success_url = reverse_lazy('dashboard:final_feedback_list')

    def get_queryset(self):
        return FeedbackQuestion.objects.filter(final_feedback_id=self.kwargs['feedback_pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        question_text = self.object.question
        feedback_pk = self.object.final_feedback.pk
        self.object.delete()
        messages.success(
            request, f'Pregunta "{question_text}" eliminada exitosamente.')
        return redirect('dashboard:final_feedback_detail', pk=feedback_pk)

# Comentarios de programa y sesión


@manager_required_class
class ProgramCommentDeleteView(View):
    """Elimina un comentario de programa y redirige a la moderación de comentarios de la sesión."""

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        session = comment.session
        module = session.module
        program = module.program
        comment.delete()
        messages.success(request, 'Comentario eliminado correctamente.')
        return redirect(reverse('dashboard:session_comment_moderation', kwargs={
            'program_pk': program.pk,
            'module_pk': module.pk,
            'session_pk': session.pk
        }))


@manager_required_class
class SessionCommentModerationView(View):
    """Lista y modera los comentarios de una sesión de programa en el dashboard."""

    def get(self, request, program_pk, module_pk, session_pk):
        session = get_object_or_404(
            Session, pk=session_pk, module_id=module_pk)
        module = session.module
        program = module.program
        root_comments = session.comments.filter(parent__isnull=True).select_related(
            'author').prefetch_related('replies')
        return render(request, 'dashboard/programs/comment_moderation.html', {
            'session': session,
            'module': module,
            'program': program,
            'root_comments': root_comments,
            'active_menu': 'program_comments',
        })


@manager_required_class
class SessionCommentReplyView(View):
    """Permite a managers responder a un comentario de sesión desde el dashboard."""

    def post(self, request, program_pk, module_pk, session_pk, parent_comment_id):
        session = get_object_or_404(
            Session, pk=session_pk, module_id=module_pk)
        parent_comment = get_object_or_404(
            Comment, pk=parent_comment_id, session=session)
        content = request.POST.get('content', '').strip()
        if not content:
            messages.error(
                request, 'El contenido de la respuesta no puede estar vacío.')
            return redirect('dashboard:session_comment_moderation', program_pk=session.module.program.pk, module_pk=module_pk, session_pk=session_pk)
        Comment.objects.create(
            session=session,
            author=request.user,
            parent=parent_comment,
            content=content
        )
        messages.success(request, 'Respuesta publicada correctamente.')
        return redirect('dashboard:session_comment_moderation', program_pk=session.module.program.pk, module_pk=module_pk, session_pk=session_pk)
