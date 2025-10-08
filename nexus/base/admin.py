# Third Party Stuff
from django.contrib import admin

# Nexus Stuff
from nexus.base.audit_models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'description', 'ip_address')
    list_filter = ('action', 'created_at', 'user')
    search_fields = ('user__email', 'description', 'ip_address')
    readonly_fields = ('id', 'user', 'action', 'description', 'ip_address', 'user_agent',
                      'content_type', 'object_id', 'changes', 'created_at', 'modified_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs
        return False
