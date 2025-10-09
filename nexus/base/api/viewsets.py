# Third Party Stuff
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# nexus Stuff
from nexus.base import response
from nexus.base.audit_models import AuditLog


# ============================================================================
# Serializers
# ============================================================================

class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model (read-only)"""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'user_name', 'action', 'content_type',
                 'content_type_name', 'object_id', 'description', 'changes',
                 'ip_address', 'user_agent', 'created_at', 'modified_at']
        read_only_fields = ['id', 'user', 'action', 'content_type', 'object_id',
                           'description', 'changes', 'ip_address', 'user_agent',
                           'created_at', 'modified_at']
        ref_name = 'AuditLog'

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return "System"

    def get_content_type_name(self, obj):
        if obj.content_type:
            return f"{obj.content_type.app_label}.{obj.content_type.model}"
        return None


# ============================================================================
# ViewSets
# ============================================================================

class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """ViewSet for AuditLog model (read-only for audit trail)"""

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name',
                    'description', 'changes', 'ip_address']
    ordering_fields = ['created_at', 'action']
    filterset_fields = ['user', 'action', 'content_type']

    def get_queryset(self):
        return AuditLog.objects.select_related('user', 'content_type').order_by('-created_at')

    @action(methods=['GET'], detail=False)
    def recent(self, request):
        """Get recent audit logs"""
        limit = int(request.query_params.get('limit', 50))
        queryset = self.filter_queryset(self.get_queryset())[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=False)
    def by_user(self, request):
        """Get audit logs for a specific user"""
        user_id = request.query_params.get('user_id')

        if not user_id:
            return response.BadRequest({'error_message': 'user_id is required'})

        queryset = self.filter_queryset(self.get_queryset()).filter(user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=False)
    def by_object(self, request):
        """Get audit logs for a specific object"""
        content_type_id = request.query_params.get('content_type_id')
        object_id = request.query_params.get('object_id')

        if not content_type_id or not object_id:
            return response.BadRequest({
                'error_message': 'content_type_id and object_id are required'
            })

        queryset = self.filter_queryset(self.get_queryset()).filter(
            content_type_id=content_type_id,
            object_id=object_id
        )
        serializer = self.get_serializer(queryset, many=True)
        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=False)
    def statistics(self, request):
        """Get audit log statistics"""
        from django.db.models import Count

        queryset = self.filter_queryset(self.get_queryset())

        # Count by action
        by_action = queryset.values('action').annotate(count=Count('id')).order_by('-count')

        # Count by user
        by_user = queryset.filter(user__isnull=False).values(
            'user__email'
        ).annotate(count=Count('id')).order_by('-count')[:10]

        # Count by content type
        by_model = queryset.filter(content_type__isnull=False).values(
            'content_type__app_label', 'content_type__model'
        ).annotate(count=Count('id')).order_by('-count')[:10]

        data = {
            'total_logs': queryset.count(),
            'by_action': list(by_action),
            'top_users': list(by_user),
            'top_models': [
                {
                    'model': f"{item['content_type__app_label']}.{item['content_type__model']}",
                    'count': item['count']
                }
                for item in by_model
            ],
        }

        return response.Ok(data)
