from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from constants.constant import UserRoles
from .models import Post, Category, Tag, Comment


def post_list(request):
    posts = Post.objects.filter(status='published').select_related(
        'author', 'category').prefetch_related('tags')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(introduction__icontains=search_query) |
            Q(body__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'search_query': search_query,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

    # Increment view count
    post.increment_view_count()

    # Get approved comments
    comments = Comment.objects.filter(
        post=post,
        status='approved',
        parent=None
    ).select_related('author').prefetch_related('replies')

    # Related posts
    related_posts = Post.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]

    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'can_comment': request.user.is_authenticated and request.user.role == UserRoles.MEMBER,
    }
    return render(request, 'blog/post_detail.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags')

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'posts': page_obj,
    }
    return render(request, 'blog/category_detail.html', context)


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(
        tags=tag,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags')

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'posts': page_obj,
    }
    return render(request, 'blog/tag_detail.html', context)


@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

    # Check if user can comment
    if request.user.role != UserRoles.MEMBER:
        messages.error(request, 'Only members can comment.')
        return redirect('blog:post_detail', slug=slug)

    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')

    if not content:
        messages.error(request, 'Comment cannot be empty.')
        return redirect('blog:post_detail', slug=slug)

    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id, post=post)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent
    )

    messages.success(
        request, 'Your comment has been submitted and is awaiting approval.')
    return redirect('blog:post_detail', slug=slug)
