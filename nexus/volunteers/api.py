# Third Party Stuff
from django.db.models import Q, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# nexus Stuff
from nexus.base import response
from nexus.volunteers import models


# ============================================================================
# Serializers
# ============================================================================

class VolunteerRoleSerializer(serializers.ModelSerializer):
    """Serializer for VolunteerRole model"""

    shifts_count = serializers.SerializerMethodField()

    class Meta:
        model = models.VolunteerRole
        fields = ['id', 'name', 'description', 'required_skills', 'volunteers_needed',
                 'is_active', 'shifts_count', 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        ref_name = 'VolunteerRole'

    def get_shifts_count(self, obj):
        return obj.shifts.count()


class VolunteerShiftSerializer(serializers.ModelSerializer):
    """Serializer for VolunteerShift model"""

    event_name = serializers.CharField(source='event.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    current_volunteers = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()

    class Meta:
        model = models.VolunteerShift
        fields = ['id', 'event', 'event_name', 'role', 'role_name', 'title',
                 'description', 'start_time', 'end_time', 'max_volunteers',
                 'status', 'location', 'current_volunteers', 'is_full',
                 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        ref_name = 'VolunteerShift'

    def get_current_volunteers(self, obj):
        return obj.current_volunteers_count()

    def get_is_full(self, obj):
        return obj.is_full()


class VolunteerAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for VolunteerAssignment model"""

    shift_title = serializers.CharField(source='shift.title', read_only=True)
    volunteer_email = serializers.EmailField(source='volunteer.email', read_only=True)
    volunteer_name = serializers.SerializerMethodField()
    hours_worked = serializers.SerializerMethodField()

    class Meta:
        model = models.VolunteerAssignment
        fields = ['id', 'shift', 'shift_title', 'volunteer', 'volunteer_email',
                 'volunteer_name', 'status', 'assigned_at', 'confirmed_at',
                 'checked_in_at', 'completed_at', 'notes', 'rating', 'feedback',
                 'hours_worked', 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at', 'assigned_at']
        ref_name = 'VolunteerAssignment'

    def get_volunteer_name(self, obj):
        return f"{obj.volunteer.first_name} {obj.volunteer.last_name}".strip() or obj.volunteer.email

    def get_hours_worked(self, obj):
        return round(obj.hours_worked(), 2)


class VolunteerTaskSerializer(serializers.ModelSerializer):
    """Serializer for VolunteerTask model"""

    event_name = serializers.CharField(source='event.name', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    assigned_by_email = serializers.EmailField(source='assigned_by.email', read_only=True)

    class Meta:
        model = models.VolunteerTask
        fields = ['id', 'event', 'event_name', 'title', 'description',
                 'assigned_to', 'assigned_to_email', 'assigned_by', 'assigned_by_email',
                 'status', 'priority', 'due_date', 'completed_at',
                 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        ref_name = 'VolunteerTask'


class VolunteerHoursSerializer(serializers.ModelSerializer):
    """Serializer for VolunteerHours model"""

    volunteer_email = serializers.EmailField(source='volunteer.email', read_only=True)
    volunteer_name = serializers.SerializerMethodField()
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = models.VolunteerHours
        fields = ['id', 'volunteer', 'volunteer_email', 'volunteer_name',
                 'event', 'event_name', 'total_hours', 'last_updated',
                 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at', 'last_updated']
        ref_name = 'VolunteerHours'

    def get_volunteer_name(self, obj):
        return f"{obj.volunteer.first_name} {obj.volunteer.last_name}".strip() or obj.volunteer.email


# ============================================================================
# ViewSets
# ============================================================================

class VolunteerRoleViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                           mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for VolunteerRole model"""

    queryset = models.VolunteerRole.objects.all()
    serializer_class = VolunteerRoleSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'required_skills']
    ordering_fields = ['name', 'volunteers_needed', 'created_at']
    filterset_fields = ['is_active']

    def get_queryset(self):
        return models.VolunteerRole.objects.prefetch_related('shifts')


class VolunteerShiftViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                            mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for VolunteerShift model"""

    queryset = models.VolunteerShift.objects.all()
    serializer_class = VolunteerShiftSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    filterset_fields = ['event', 'role', 'status']

    def get_queryset(self):
        return models.VolunteerShift.objects.select_related('event', 'role').prefetch_related('assignments')

    @action(methods=['GET'], detail=False)
    def available(self, request):
        """Get available shifts that are not full"""
        queryset = self.filter_queryset(self.get_queryset())
        available_shifts = [shift for shift in queryset if not shift.is_full()]
        serializer = self.get_serializer(available_shifts, many=True)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def assign_volunteer(self, request, pk=None):
        """Assign a volunteer to this shift"""
        shift = self.get_object()

        if shift.is_full():
            return response.BadRequest({'error_message': 'Shift is already full'})

        volunteer_id = request.data.get('volunteer_id')
        if not volunteer_id:
            return response.BadRequest({'error_message': 'volunteer_id is required'})

        from nexus.users.models import User
        try:
            volunteer = User.objects.get(id=volunteer_id)
        except User.DoesNotExist:
            return response.BadRequest({'error_message': 'Volunteer not found'})

        # Check if already assigned
        if models.VolunteerAssignment.objects.filter(shift=shift, volunteer=volunteer).exists():
            return response.BadRequest({'error_message': 'Volunteer already assigned to this shift'})

        assignment = models.VolunteerAssignment.objects.create(
            shift=shift,
            volunteer=volunteer,
            status=models.VolunteerAssignment.STATUS_CHOICES.PENDING
        )

        assignment_serializer = VolunteerAssignmentSerializer(assignment)
        return response.Ok(assignment_serializer.data)


class VolunteerAssignmentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                                 mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for VolunteerAssignment model"""

    queryset = models.VolunteerAssignment.objects.all()
    serializer_class = VolunteerAssignmentSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['volunteer__email', 'volunteer__first_name', 'volunteer__last_name', 'shift__title']
    ordering_fields = ['assigned_at', 'confirmed_at', 'checked_in_at', 'completed_at']
    filterset_fields = ['shift', 'volunteer', 'status']

    def get_queryset(self):
        return models.VolunteerAssignment.objects.select_related('shift', 'volunteer')

    @action(methods=['POST'], detail=True)
    def confirm(self, request, pk=None):
        """Confirm a volunteer assignment"""
        assignment = self.get_object()
        assignment.status = models.VolunteerAssignment.STATUS_CHOICES.CONFIRMED
        assignment.confirmed_at = timezone.now()
        assignment.save()

        serializer = self.get_serializer(assignment)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def check_in(self, request, pk=None):
        """Check in a volunteer"""
        assignment = self.get_object()
        assignment.status = models.VolunteerAssignment.STATUS_CHOICES.CHECKED_IN
        assignment.checked_in_at = timezone.now()
        assignment.save()

        serializer = self.get_serializer(assignment)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def complete(self, request, pk=None):
        """Mark assignment as completed"""
        assignment = self.get_object()
        assignment.status = models.VolunteerAssignment.STATUS_CHOICES.COMPLETED
        assignment.completed_at = timezone.now()
        assignment.save()

        # Update volunteer hours
        hours_record, created = models.VolunteerHours.objects.get_or_create(
            volunteer=assignment.volunteer,
            event=assignment.shift.event
        )
        hours_record.recalculate_hours()

        serializer = self.get_serializer(assignment)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def cancel(self, request, pk=None):
        """Cancel a volunteer assignment"""
        assignment = self.get_object()
        assignment.status = models.VolunteerAssignment.STATUS_CHOICES.CANCELLED
        assignment.save()

        serializer = self.get_serializer(assignment)
        return response.Ok(serializer.data)


class VolunteerTaskViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                           mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for VolunteerTask model"""

    queryset = models.VolunteerTask.objects.all()
    serializer_class = VolunteerTaskSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']
    filterset_fields = ['event', 'assigned_to', 'assigned_by', 'status', 'priority']

    def get_queryset(self):
        return models.VolunteerTask.objects.select_related('event', 'assigned_to', 'assigned_by')

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(methods=['POST'], detail=True)
    def complete(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = models.VolunteerTask.STATUS_CHOICES.COMPLETED
        task.completed_at = timezone.now()
        task.save()

        serializer = self.get_serializer(task)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def assign(self, request, pk=None):
        """Assign task to a volunteer"""
        task = self.get_object()
        volunteer_id = request.data.get('volunteer_id')

        if not volunteer_id:
            return response.BadRequest({'error_message': 'volunteer_id is required'})

        from nexus.users.models import User
        try:
            volunteer = User.objects.get(id=volunteer_id)
            task.assigned_to = volunteer
            task.save()

            serializer = self.get_serializer(task)
            return response.Ok(serializer.data)
        except User.DoesNotExist:
            return response.BadRequest({'error_message': 'Volunteer not found'})


class VolunteerHoursViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """ViewSet for VolunteerHours model (read-only)"""

    queryset = models.VolunteerHours.objects.all()
    serializer_class = VolunteerHoursSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['volunteer__email', 'volunteer__first_name', 'volunteer__last_name']
    ordering_fields = ['total_hours', 'last_updated']
    filterset_fields = ['volunteer', 'event']

    def get_queryset(self):
        return models.VolunteerHours.objects.select_related('volunteer', 'event')

    @action(methods=['POST'], detail=True)
    def recalculate(self, request, pk=None):
        """Recalculate volunteer hours"""
        hours_record = self.get_object()
        hours_record.recalculate_hours()

        serializer = self.get_serializer(hours_record)
        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=False)
    def leaderboard(self, request):
        """Get volunteer leaderboard by hours"""
        event_id = request.query_params.get('event')

        queryset = self.get_queryset()
        if event_id:
            queryset = queryset.filter(event_id=event_id)

        queryset = queryset.order_by('-total_hours')[:20]
        serializer = self.get_serializer(queryset, many=True)

        return response.Ok(serializer.data)
