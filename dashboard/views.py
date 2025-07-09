from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.http import JsonResponse

from constants.constant import UserRoles
from .decorators import manager_required_class
from .forms import UserEditForm, ProfileEditForm, UserFilterForm

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
            active_users=Count('id', filter=Q(is_active=True) & ~Q(role=UserRoles.MANAGER)),
            inactive_users=Count('id', filter=Q(is_active=False) & ~Q(role=UserRoles.MANAGER))
        )
        
        # Get recent users (last 5, excluding managers)
        recent_users = User.objects.exclude(
            Q(id=request.user.id) | Q(role=UserRoles.MANAGER)
        ).order_by('-date_joined')[:5]
        
        context = {
            'user_stats': user_stats,
            'recent_users': recent_users,
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
        queryset = User.objects.exclude(id=self.request.user.id).select_related('profile')
        
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
            context['profile_form'] = ProfileEditForm(self.request.POST, instance=self.object.profile)
        else:
            context['profile_form'] = ProfileEditForm(instance=self.object.profile)
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
