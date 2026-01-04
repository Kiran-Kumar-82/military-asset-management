import logging
from django.utils.deprecation import MiddlewareMixin

audit_logger = logging.getLogger('audit')


class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to log all requests for auditing purposes"""
    
    def process_request(self, request):
        # Store request start time
        request.audit_start_time = None
        return None
    
    def process_response(self, request, response):
        # Log authenticated requests to protected views
        if request.user.is_authenticated and hasattr(request, 'user'):
            # Exclude static files and media
            if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                audit_logger.info(
                    f"User: {request.user.username} | "
                    f"Method: {request.method} | "
                    f"Path: {request.path} | "
                    f"Status: {response.status_code} | "
                    f"IP: {self.get_client_ip(request)}"
                )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
