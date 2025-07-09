from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.views import View
from django.urls import reverse_lazy
from django.http import JsonResponse

from constants.constant import UserRoles
from .decorators import manager_required_class
from .forms import UserEditForm, ProfileEditForm, UserFilterForm, BlogPostForm, CategoryForm, TagForm
from blog.models import Post, Category, Tag, Comment

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
            'total_comments': Comment.objects.count(),
            'pending_comments': Comment.objects.filter(status='pending').count(),
            'approved_comments': Comment.objects.filter(status='approved').count(),
            'spam_comments': Comment.objects.filter(status='spam').count(),
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
        recent_comments = Comment.objects.select_related(
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

    model = Comment
    template_name = 'dashboard/blog/comment_moderation.html'
    context_object_name = 'comments'
    paginate_by = 20

    def get_queryset(self):
        return Comment.objects.select_related('author', 'post').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_comments'] = Comment.objects.filter(
            status='pending').count()
        context['approved_comments'] = Comment.objects.filter(
            status='approved').count()
        context['spam_comments'] = Comment.objects.filter(
            status='spam').count()
        return context


@manager_required_class
class CommentApproveView(View):
    """Approve a comment."""

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.status = 'approved'
        comment.save()
        messages.success(request, 'Comentario aprobado exitosamente.')
        return redirect('dashboard:comment_moderation')


@manager_required_class
class CommentRejectView(View):
    """Reject a comment (mark as spam)."""

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.status = 'spam'
        comment.save()
        messages.success(request, 'Comentario marcado como spam.')
        return redirect('dashboard:comment_moderation')


@manager_required_class
class CommentDeleteView(DeleteView):
    """Delete a comment."""

    model = Comment
    success_url = reverse_lazy('dashboard:comment_moderation')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(self.success_url)
