"""
Custom permission classes for RBAC
"""
from rest_framework import permissions
from .models import Role


class IsAdmin(permissions.BasePermission):
    """Only Admin users can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsBaseCommander(permissions.BasePermission):
    """Base Commander or Admin can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_admin() or request.user.is_base_commander()
        )


class IsLogisticsOfficer(permissions.BasePermission):
    """Logistics Officer or Admin can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_admin() or request.user.is_logistics_officer()
        )


class IsAdminOrLogisticsOfficer(permissions.BasePermission):
    """Admin or Logistics Officer can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_admin() or request.user.is_logistics_officer()
        )


class BaseAccessPermission(permissions.BasePermission):
    """
    Base Commanders can only access their assigned base.
    Admins can access all bases.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin():
            return True
        
        if request.user.is_base_commander():
            # Base Commanders can only access their assigned base
            if hasattr(obj, 'base'):
                return obj.base == request.user.assigned_base
            elif hasattr(obj, 'assigned_base'):
                return obj.assigned_base == request.user.assigned_base
            elif obj == request.user.assigned_base:
                return True
        
        return False


