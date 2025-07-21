from django.urls import path
from dashboard.views import DashboardIndexView

urlpatterns = [
    path('', DashboardIndexView.as_view(), name='dashboard'),
]
