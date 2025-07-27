from django.urls import path, include

from .user_urls import urlpatterns as user_urls
from .blog_urls import urlpatterns as blog_urls
from .program_urls import urlpatterns as program_urls
from .newsletter_urls import urlpatterns as newsletter_urls
from .dashboard_urls import urlpatterns as dashboard_urls
from .event_urls import urlpatterns as event_urls

app_name = "dashboard"

urlpatterns = []
urlpatterns.extend(user_urls)
urlpatterns.extend(blog_urls)
urlpatterns.extend(program_urls)
urlpatterns.extend(newsletter_urls)
urlpatterns.extend(dashboard_urls)
urlpatterns.extend(event_urls)
