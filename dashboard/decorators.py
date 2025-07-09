from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

from constants.constant import UserRoles


def manager_required(view_func):
    """
    Decorator that checks if the user has manager role.
    Redirects to home page if user doesn't have manager role.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if request.user.role != UserRoles.MANAGER:
            return redirect('public:index')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def manager_required_class(view_class):
    """
    Class decorator that checks if the user has manager role.
    For use with class-based views.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if request.user.role != UserRoles.MANAGER:
            return redirect('public:index')
        
        return super(view_class, self).dispatch(request, *args, **kwargs)
    
    view_class.dispatch = dispatch
    return view_class