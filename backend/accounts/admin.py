from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'assigned_base', 'is_staff')
    list_filter = ('role', 'assigned_base', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Military Assignment', {'fields': ('role', 'assigned_base')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Military Assignment', {'fields': ('role', 'assigned_base')}),
    )


