from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.views import View
from django.urls import reverse_lazy
from blog.models import Post, Category, Tag, Comment as BlogComment
from dashboard.forms import BlogPostForm, CategoryForm, TagForm
from constants.constant import manager_required_class, manager_required


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


@require_http_methods(["POST", "DELETE"])
@manager_required
def delete_program_comment(request, pk):
    if request.method == "POST" and request.POST.get("_method") != "DELETE":
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)
    try:
        comment = BlogComment.objects.get(pk=pk)
        comment.delete()
        return JsonResponse({'success': True})
    except BlogComment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comentario no encontrado.'}, status=404)
