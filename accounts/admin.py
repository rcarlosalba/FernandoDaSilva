from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    """
    Inline representation of the Profile model for the User admin page.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom UserAdmin for our email-based User model.
    """
    inlines = (ProfileInline,)

    # Fields to display in the user list
    list_display = ('email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff',
                   'is_superuser', 'date_joined')
    search_fields = ('email',)
    ordering = ('email',)

    # Fieldsets for the user detail page - ADAPTADOS PARA TU MODELO
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('role',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets for adding a new user - SIN CAMPOS QUE NO EXISTEN
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin for Profile model.
    """
    list_display = ('user', 'first_name', 'last_name', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user', 'first_name', 'last_name')}),
        (_('Additional Info'), {'fields': ('bio', 'avatar')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
