"""
Middleware for role-based access control
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import Role


class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware to enforce role-based access at the request level.
    This provides an additional layer of security beyond view-level permissions.
    """
    
    # Define which roles can access which endpoints
    ADMIN_ONLY_ENDPOINTS = [
        '/api/accounts/users/',
        '/api/accounts/roles/',
    ]
    
    def process_request(self, request):
        # Skip for unauthenticated users (handled by DRF permissions)
        if not request.user.is_authenticated:
            return None
        
        # Skip for admin endpoints that are handled by view permissions
        if request.path.startswith('/api/admin/'):
            return None
        
        # Check admin-only endpoints
        for endpoint in self.ADMIN_ONLY_ENDPOINTS:
            if request.path.startswith(endpoint) and not request.user.is_admin():
                return JsonResponse(
                    {'error': 'Insufficient permissions. Admin access required.'},
                    status=403
                )
        
        return None


