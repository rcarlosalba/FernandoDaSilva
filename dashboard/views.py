from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_http_methods, require_POST
from django.utils.decorators import method_decorator
from constants.constant import UserRoles, manager_required_class, manager_required
from .forms import UserEditForm, ProfileEditForm, UserFilterForm, BlogPostForm, CategoryForm, TagForm
from blog.models import Post, Category, Tag, Comment as BlogComment
from programs.models import (
    Program, Module, Session, Material, Assignment,
    FinalFeedback, FeedbackQuestion, FeedbackResponse, Comment
)
from programs.forms import (
    ProgramForm, ModuleForm, SessionForm, MaterialForm,
    AssignmentForm, FinalFeedbackForm, FeedbackQuestionForm
)

User = get_user_model()


@manager_required_class
class DashboardIndexView(View):
    """Main dashboard view with overview statistics."""

    def get(self, request):
        # Get user statistics (excluding managers from user count)
        user_stats = User.objects.aggregate(
            total_users=Count('id', filter=~Q(role=UserRoles.MANAGER)),
            subscribers=Count('id', filter=Q(role=UserRoles.SUBSCRIBER)),
            members=Count('id', filter=Q(role=UserRoles.MEMBER)),
            students=Count('id', filter=Q(role=UserRoles.STUDENT)),
            assistants=Count('id', filter=Q(role=UserRoles.ASSISTANT)),
            active_users=Count('id', filter=Q(is_active=True)
                               & ~Q(role=UserRoles.MANAGER)),
            inactive_users=Count('id', filter=Q(
                is_active=False) & ~Q(role=UserRoles.MANAGER))
        )

        # Get blog statistics
        blog_stats = {
            'total_posts': Post.objects.count(),
            'published_posts': Post.objects.filter(status='published').count(),
            'draft_posts': Post.objects.filter(status='draft').count(),
            'total_categories': Category.objects.count(),
            'total_tags': Tag.objects.count(),
            'total_comments': BlogComment.objects.count(),
            'pending_comments': BlogComment.objects.filter(status='pending').count(),
            'approved_comments': BlogComment.objects.filter(status='approved').count(),
            'spam_comments': BlogComment.objects.filter(status='spam').count(),
            'total_views': Post.objects.aggregate(total_views=Count('view_count'))['total_views'] or 0,
        }

        # Get recent users (last 5, excluding managers)
        recent_users = User.objects.exclude(
            Q(id=request.user.id) | Q(role=UserRoles.MANAGER)
        ).order_by('-date_joined')[:5]

        # Get recent posts (last 5)
        recent_posts = Post.objects.select_related(
            'author', 'category').order_by('-created_at')[:5]

        # Get recent comments (last 5)
        recent_comments = BlogComment.objects.select_related(
            'author', 'post').order_by('-created_at')[:5]

        # Get top categories by post count
        top_categories = Category.objects.annotate(
            post_count=Count('posts')
        ).order_by('-post_count')[:5]

        # Get top tags by post count
        top_tags = Tag.objects.annotate(
            post_count=Count('posts')
        ).order_by('-post_count')[:5]

        context = {
            'user_stats': user_stats,
            'blog_stats': blog_stats,
            'recent_users': recent_users,
            'recent_posts': recent_posts,
            'recent_comments': recent_comments,
            'top_categories': top_categories,
            'top_tags': top_tags,
        }

        return render(request, 'dashboard/index.html', context)


@manager_required_class
class UserListView(ListView):
    """List all users with filtering capabilities."""

    model = User
    template_name = 'dashboard/users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.exclude(
            id=self.request.user.id).select_related('profile')

        # Apply filters
        form = UserFilterForm(self.request.GET)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            search = form.cleaned_data.get('search')

            if role:
                queryset = queryset.filter(role=role)

            if search:
                queryset = queryset.filter(
                    Q(email__icontains=search) |
                    Q(profile__first_name__icontains=search) |
                    Q(profile__last_name__icontains=search)
                )

        return queryset.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = UserFilterForm(self.request.GET)
        return context


@manager_required_class
class UserDetailView(DetailView):
    """View detailed information about a specific user."""

    model = User
    template_name = 'dashboard/users/user_detail.html'
    context_object_name = 'user_obj'

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id).select_related('profile')


@manager_required_class
class UserEditView(UpdateView):
    """Edit user information."""

    model = User
    form_class = UserEditForm
    template_name = 'dashboard/users/user_edit.html'
    context_object_name = 'user_obj'

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = ProfileEditForm(
                self.request.POST, instance=self.object.profile)
        else:
            context['profile_form'] = ProfileEditForm(
                instance=self.object.profile)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']

        if profile_form.is_valid():
            self.object = form.save()
            profile_form.instance = self.object.profile
            profile_form.save()
            messages.success(self.request, 'Usuario actualizado exitosamente.')
            return redirect('dashboard:user_detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:user_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class UserDeleteView(DeleteView):
    """Delete a user."""

    model = User
    template_name = 'dashboard/users/user_delete.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('dashboard:user_list')

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        email = self.object.email
        self.object.delete()
        messages.success(request, f'Usuario {email} eliminado exitosamente.')
        return redirect(self.success_url)


# Blog Management Views

@manager_required_class
class BlogPostListView(ListView):
    """List all blog posts for management."""

    model = Post
    template_name = 'dashboard/blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.select_related('author', 'category').prefetch_related('tags').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.count()
        context['published_posts'] = Post.objects.filter(
            status='published').count()
        context['draft_posts'] = Post.objects.filter(status='draft').count()
        return context


@manager_required_class
class BlogPostDetailView(DetailView):
    """View detailed information about a specific blog post."""

    model = Post
    template_name = 'dashboard/blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.select_related('author', 'category').prefetch_related('tags')


@manager_required_class
class BlogPostCreateView(CreateView):
    """Create a new blog post."""

    model = Post
    template_name = 'dashboard/blog/post_form.html'
    form_class = BlogPostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Artículo creado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:blog_post_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class BlogPostUpdateView(UpdateView):
    """Update an existing blog post."""

    model = Post
    template_name = 'dashboard/blog/post_form.html'
    form_class = BlogPostForm

    def form_valid(self, form):
        messages.success(self.request, 'Artículo actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:blog_post_detail', kwargs={'pk': self.object.pk})


@manager_required_class
class BlogPostDeleteView(DeleteView):
    """Delete a blog post."""

    model = Post
    success_url = reverse_lazy('dashboard:blog_post_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = self.object.title
        self.object.delete()
        messages.success(
            request, f'Artículo "{title}" eliminado exitosamente.')
        return redirect(self.success_url)


@manager_required_class
class CategoryListView(ListView):
    """List all categories for management."""

    model = Category
    template_name = 'dashboard/blog/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        return Category.objects.annotate(post_count=Count('posts')).order_by('name')


@manager_required_class
class CategoryDetailView(DetailView):
    """View detailed information about a specific category."""

    model = Category
    template_name = 'dashboard/blog/category_detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        return Category.objects.annotate(post_count=Count('posts'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.select_related(
            'author').order_by('-created_at')[:10]

        # Add statistics
        context['published_posts_count'] = self.object.posts.filter(
            status='published').count()
        context['draft_posts_count'] = self.object.posts.filter(
            status='draft').count()

        return context


@manager_required_class
class CategoryCreateView(CreateView):
    """Create a new category."""

    model = Category
    template_name = 'dashboard/blog/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('dashboard:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada exitosamente.')
        return super().form_valid(form)


@manager_required_class
class CategoryUpdateView(UpdateView):
    """Update an existing category."""

    model = Category
    template_name = 'dashboard/blog/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('dashboard:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return super().form_valid(form)


@manager_required_class
class CategoryDeleteView(DeleteView):
    """Delete a category."""

    model = Category
    success_url = reverse_lazy('dashboard:category_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = self.object.name
        self.object.delete()
        messages.success(
            request, f'Categoría "{name}" eliminada exitosamente.')
        return redirect(self.success_url)


@manager_required_class
class TagListView(ListView):
    """List all tags for management."""

    model = Tag
    template_name = 'dashboard/blog/tag_list.html'
    context_object_name = 'tags'
    paginate_by = 20

    def get_queryset(self):
        return Tag.objects.annotate(post_count=Count('posts')).order_by('name')


@manager_required_class
class TagDetailView(DetailView):
    """View detailed information about a specific tag."""

    model = Tag
    template_name = 'dashboard/blog/tag_detail.html'
    context_object_name = 'tag'

    def get_queryset(self):
        return Tag.objects.annotate(post_count=Count('posts'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.select_related(
            'author').order_by('-created_at')[:10]

        # Add statistics
        context['published_posts_count'] = self.object.posts.filter(
            status='published').count()
        context['draft_posts_count'] = self.object.posts.filter(
            status='draft').count()

        return context


@manager_required_class
class TagCreateView(CreateView):
    """Create a new tag."""

    model = Tag
    template_name = 'dashboard/blog/tag_form.html'
    form_class = TagForm
    success_url = reverse_lazy('dashboard:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Etiqueta creada exitosamente.')
        return super().form_valid(form)


@manager_required_class
class TagUpdateView(UpdateView):
    """Update an existing tag."""

    model = Tag
    template_name = 'dashboard/blog/tag_form.html'
    form_class = TagForm
    success_url = reverse_lazy('dashboard:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Etiqueta actualizada exitosamente.')
        return super().form_valid(form)


@manager_required_class
class TagDeleteView(DeleteView):
    """Delete a tag."""

    model = Tag
    success_url = reverse_lazy('dashboard:tag_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = self.object.name
        self.object.delete()
        messages.success(request, f'Etiqueta "{name}" eliminada exitosamente.')
        return redirect(self.success_url)


@manager_required_class
class CommentModerationView(ListView):
    """List all comments for moderation."""

    model = BlogComment
    template_name = 'dashboard/blog/comment_moderation.html'
    context_object_name = 'comments'
    paginate_by = 20

    def get_queryset(self):
        return BlogComment.objects.select_related('author', 'post').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_comments'] = BlogComment.objects.filter(
            status='pending').count()
        context['approved_comments'] = BlogComment.objects.filter(
            status='approved').count()
        context['spam_comments'] = BlogComment.objects.filter(
            status='spam').count()
        return context


@manager_required_class
class CommentApproveView(View):
    """Approve a comment."""

    def post(self, request, pk):
        comment = get_object_or_404(BlogComment, pk=pk)
        comment.status = 'approved'
        comment.save()
        messages.success(request, 'Comentario aprobado exitosamente.')
        return redirect('dashboard:comment_moderation')


@manager_required_class
class CommentRejectView(View):
    """Reject a comment (mark as spam)."""

    def post(self, request, pk):
        comment = get_object_or_404(BlogComment, pk=pk)
        comment.status = 'spam'
        comment.save()
        messages.success(request, 'Comentario marcado como spam.')
        return redirect('dashboard:comment_moderation')


@manager_required_class
class CommentDeleteView(DeleteView):
    """Delete a comment."""

    model = BlogComment
    success_url = reverse_lazy('dashboard:comment_moderation')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(self.success_url)


# Program Management Views

@manager_required_class
class ProgramListView(ListView):
    """List all programs for management."""

    model = Program
    template_name = 'dashboard/programs/program_list.html'
    context_object_name = 'programs'
    paginate_by = 20

    def get_queryset(self):
        return Program.objects.prefetch_related('modules').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_programs'] = Program.objects.count()
        context['total_modules'] = Module.objects.count()
        context['total_sessions'] = Session.objects.count()
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


# Assignment Management Views (Manager only)

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
        # Cambiar el rol del usuario asignado a 'student' si no lo es
        student = form.cleaned_data['student']
        from constants.constant import UserRoles
        if student.role != UserRoles.STUDENT:
            student.role = UserRoles.STUDENT
            student.save()
        messages.success(self.request, 'Asignación creada exitosamente.')
        return super().form_valid(form)

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

        # Create a new feedback form
        new_feedback = FinalFeedback.objects.create(
            program=original_feedback.program,
            title=f"{original_feedback.title} (Copia)",
            description=original_feedback.description
        )

        # Duplicate all questions
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
        # Set order to next available number
        max_order = FeedbackQuestion.objects.filter(
            final_feedback_id=self.kwargs['feedback_pk']).aggregate(
            max_order=models.Max('order'))['max_order'] or 0
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


@require_http_methods(["POST", "DELETE"])
@manager_required
def delete_program_comment(request, pk):
    # Permitir POST con _method=DELETE por compatibilidad con formularios
    if request.method == "POST" and request.POST.get("_method") != "DELETE":
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)
    try:
        comment = BlogComment.objects.get(pk=pk)
        comment.delete()
        return JsonResponse({'success': True})
    except BlogComment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comentario no encontrado.'}, status=404)


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
