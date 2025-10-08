# Third Party Stuff
from django.utils.deprecation import MiddlewareMixin

# Nexus Stuff
from nexus.base.audit_models import AuditLog


class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to automatically log certain actions"""

    def process_request(self, request):
        # Store request info for later use
        request.audit_ip = self.get_client_ip(request)
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')

    def process_response(self, request, response):
        # Log authentication actions
        if hasattr(request, 'user') and request.user.is_authenticated:
            path = request.path
            method = request.method

            # Log login/logout
            if 'login' in path and method == 'POST' and response.status_code == 200:
                AuditLog.log_action(
                    user=request.user,
                    action='login',
                    description=f'User logged in from {request.audit_ip}',
                    ip_address=request.audit_ip,
                    user_agent=request.audit_user_agent
                )
            elif 'logout' in path and method == 'POST':
                AuditLog.log_action(
                    user=request.user,
                    action='logout',
                    description=f'User logged out',
                    ip_address=request.audit_ip,
                    user_agent=request.audit_user_agent
                )

        return response

    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
