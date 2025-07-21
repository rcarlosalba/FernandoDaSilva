from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.views import View
from constants.constant import UserRoles, manager_required_class
from blog.models import Post, Category, Tag, Comment as BlogComment

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
