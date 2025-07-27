from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.views import View
from constants.constant import UserRoles, manager_required_class
from blog.models import Post, Category, Tag, Comment as BlogComment
from events.models import Event, Registration
from programs.models import Program, Module, Session, Assignment, Material, FinalFeedback, Comment as ProgramComment
from newsletter.models import Newsletter, Subscriber

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

        # Get event statistics
        total_events = Event.objects.count()
        published_events = Event.objects.filter(status='published').count()
        draft_events = Event.objects.filter(status='draft').count()
        upcoming_events = Event.objects.filter(start_date__gt=request.now if hasattr(
            request, 'now') else None).count() if hasattr(request, 'now') else Event.objects.count()
        total_registrations = Registration.objects.count()
        event_stats = {
            'total_events': total_events,
            'published_events': published_events,
            'draft_events': draft_events,
            'upcoming_events': upcoming_events,
            'total_registrations': total_registrations,
        }

        # Get program statistics
        program_stats = {
            'total_programs': Program.objects.count(),
            'total_modules': Module.objects.count(),
            'total_sessions': Session.objects.count(),
            'total_assignments': Assignment.objects.count(),
            'total_materials': Material.objects.count(),
            'total_feedbacks': FinalFeedback.objects.count(),
            'total_comments': ProgramComment.objects.count(),
        }

        # Get newsletter statistics
        newsletter_stats = {
            'total_newsletters': Newsletter.objects.count(),
            'total_subscribers': Subscriber.objects.filter(is_subscribed=True).count(),
        }

        context = {
            'user_stats': user_stats,
            'blog_stats': blog_stats,
            'event_stats': event_stats,
            'program_stats': program_stats,
            'newsletter_stats': newsletter_stats,
        }

        return render(request, 'dashboard/index.html', context)
