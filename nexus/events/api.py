# Third Party Stuff
from django.db.models import Q, Count, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# nexus Stuff
from nexus.base import response
from nexus.events import models


# ============================================================================
# Serializers
# ============================================================================

class VenueSerializer(serializers.ModelSerializer):
    """Serializer for Venue model with nested relationships"""

    sessions_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Venue
        fields = ['id', 'event', 'name', 'capacity', 'description', 'floor',
                 'has_projector', 'has_microphone', 'has_whiteboard',
                 'additional_equipment', 'sessions_count', 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        ref_name = 'EventVenue'

    def get_sessions_count(self, obj):
        return obj.sessions.count()


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model with nested relationships"""

    event_name = serializers.CharField(source='event.name', read_only=True)
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)
    speaker_emails = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = models.Session
        fields = ['id', 'event', 'event_name', 'proposal', 'proposal_title',
                 'venue', 'venue_name', 'title', 'description', 'session_type',
                 'start_time', 'end_time', 'speakers', 'speaker_emails',
                 'is_recorded', 'recording_url', 'slides_url', 'duration_minutes',
                 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        ref_name = 'EventSession'

    def get_speaker_emails(self, obj):
        return [speaker.email for speaker in obj.speakers.all()]

    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return int(delta.total_seconds() / 60)
        return 0


class AttendeeSerializer(serializers.ModelSerializer):
    """Serializer for Attendee model with nested relationships"""

    event_name = serializers.CharField(source='event.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Attendee
        fields = ['id', 'event', 'event_name', 'user', 'user_email', 'user_name',
                 'status', 'registration_date', 'checked_in_at', 'ticket_number',
                 'ticket_type', 'dietary_requirements', 'accessibility_requirements',
                 'special_requests', 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at', 'registration_date']
        ref_name = 'EventAttendee'

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class SponsorSerializer(serializers.ModelSerializer):
    """Serializer for Sponsor model"""

    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = models.Sponsor
        fields = ['id', 'event', 'event_name', 'name', 'tier', 'logo', 'website_url',
                 'description', 'contact_name', 'contact_email', 'display_order',
                 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        ref_name = 'EventSponsor'


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model with nested relationships"""

    # Nested serializers for related objects
    venues = VenueSerializer(many=True, read_only=True)
    sessions = SessionSerializer(many=True, read_only=True)
    sponsors = SponsorSerializer(many=True, read_only=True)

    # Counts
    attendees_count = serializers.SerializerMethodField()
    sessions_count = serializers.SerializerMethodField()
    sponsors_count = serializers.SerializerMethodField()
    venues_count = serializers.SerializerMethodField()

    # Status info
    is_registration_open = serializers.SerializerMethodField()
    is_cfp_open = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = ['id', 'name', 'slug', 'description', 'tagline',
                 'start_date', 'end_date', 'registration_start', 'registration_end',
                 'cfp_start', 'cfp_end', 'venue_name', 'venue_address', 'city',
                 'country', 'is_virtual', 'virtual_platform', 'status',
                 'max_attendees', 'website_url', 'logo', 'banner',
                 'venues', 'sessions', 'sponsors', 'attendees_count',
                 'sessions_count', 'sponsors_count', 'venues_count',
                 'is_registration_open', 'is_cfp_open',
                 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']
        ref_name = 'Event'

    def get_attendees_count(self, obj):
        return obj.attendees.filter(
            status__in=[models.Attendee.STATUS_CHOICES.REGISTERED,
                       models.Attendee.STATUS_CHOICES.CONFIRMED,
                       models.Attendee.STATUS_CHOICES.CHECKED_IN]
        ).count()

    def get_sessions_count(self, obj):
        return obj.sessions.count()

    def get_sponsors_count(self, obj):
        return obj.sponsors.count()

    def get_venues_count(self, obj):
        return obj.venues.count()

    def get_is_registration_open(self, obj):
        from django.utils import timezone
        now = timezone.now()
        return obj.registration_start <= now <= obj.registration_end

    def get_is_cfp_open(self, obj):
        from django.utils import timezone
        if not obj.cfp_start or not obj.cfp_end:
            return False
        now = timezone.now()
        return obj.cfp_start <= now <= obj.cfp_end


# ============================================================================
# ViewSets
# ============================================================================

class EventViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for Event model with full CRUD operations"""

    queryset = models.Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'city', 'country']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'name']
    filterset_fields = ['status', 'is_virtual', 'city', 'country']
    lookup_field = 'slug'

    def get_queryset(self):
        return models.Event.objects.prefetch_related(
            'venues', 'sessions', 'sponsors', 'attendees'
        ).all()

    @action(methods=['GET'], detail=True)
    def schedule(self, request, slug=None):
        """Get event schedule grouped by date"""
        event = self.get_object()
        sessions = event.sessions.select_related('venue', 'proposal').prefetch_related('speakers').order_by('start_time')

        # Group by date
        schedule_by_date = {}
        for session in sessions:
            date_key = session.start_time.date().isoformat()
            if date_key not in schedule_by_date:
                schedule_by_date[date_key] = []

            schedule_by_date[date_key].append({
                'id': str(session.id),
                'title': session.title,
                'session_type': session.session_type,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat(),
                'venue': session.venue.name,
                'speakers': [s.email for s in session.speakers.all()],
            })

        return response.Ok(schedule_by_date)

    @action(methods=['GET'], detail=True)
    def statistics(self, request, slug=None):
        """Get event statistics"""
        event = self.get_object()

        attendees = event.attendees.all()
        sessions = event.sessions.all()

        stats = {
            'event_name': event.name,
            'total_attendees': attendees.count(),
            'registered': attendees.filter(status=models.Attendee.STATUS_CHOICES.REGISTERED).count(),
            'confirmed': attendees.filter(status=models.Attendee.STATUS_CHOICES.CONFIRMED).count(),
            'checked_in': attendees.filter(status=models.Attendee.STATUS_CHOICES.CHECKED_IN).count(),
            'total_sessions': sessions.count(),
            'sessions_by_type': {
                session_type: sessions.filter(session_type=session_type).count()
                for session_type, _ in models.Session.SESSION_TYPE_CHOICES
            },
            'total_sponsors': event.sponsors.count(),
            'sponsors_by_tier': {
                tier: event.sponsors.filter(tier=tier).count()
                for tier, _ in models.Sponsor.TIER_CHOICES
            },
            'total_venues': event.venues.count(),
        }

        return response.Ok(stats)


class VenueViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for Venue model"""

    queryset = models.Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'floor']
    ordering_fields = ['name', 'capacity', 'created_at']
    filterset_fields = ['event', 'has_projector', 'has_microphone', 'has_whiteboard']

    def get_queryset(self):
        return models.Venue.objects.select_related('event').prefetch_related('sessions')


class SessionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for Session model"""

    queryset = models.Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    filterset_fields = ['event', 'venue', 'session_type', 'is_recorded']

    def get_queryset(self):
        return models.Session.objects.select_related(
            'event', 'venue', 'proposal'
        ).prefetch_related('speakers')

    @action(methods=['POST'], detail=True)
    def add_speaker(self, request, pk=None):
        """Add a speaker to the session"""
        session = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return response.BadRequest({'error_message': 'user_id is required'})

        from nexus.users.models import User
        try:
            user = User.objects.get(id=user_id)
            session.speakers.add(user)
            serializer = self.get_serializer(session)
            return response.Ok(serializer.data)
        except User.DoesNotExist:
            return response.BadRequest({'error_message': 'User not found'})

    @action(methods=['POST'], detail=True)
    def remove_speaker(self, request, pk=None):
        """Remove a speaker from the session"""
        session = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return response.BadRequest({'error_message': 'user_id is required'})

        from nexus.users.models import User
        try:
            user = User.objects.get(id=user_id)
            session.speakers.remove(user)
            serializer = self.get_serializer(session)
            return response.Ok(serializer.data)
        except User.DoesNotExist:
            return response.BadRequest({'error_message': 'User not found'})


class AttendeeViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for Attendee model"""

    queryset = models.Attendee.objects.all()
    serializer_class = AttendeeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'ticket_number']
    ordering_fields = ['registration_date', 'checked_in_at', 'created_at']
    filterset_fields = ['event', 'status', 'ticket_type']

    def get_queryset(self):
        return models.Attendee.objects.select_related('event', 'user')

    @action(methods=['POST'], detail=True)
    def check_in(self, request, pk=None):
        """Check in an attendee"""
        from django.utils import timezone

        attendee = self.get_object()
        if attendee.status == models.Attendee.STATUS_CHOICES.CHECKED_IN:
            return response.BadRequest({'error_message': 'Attendee already checked in'})

        attendee.status = models.Attendee.STATUS_CHOICES.CHECKED_IN
        attendee.checked_in_at = timezone.now()
        attendee.save()

        serializer = self.get_serializer(attendee)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def confirm(self, request, pk=None):
        """Confirm an attendee registration"""
        attendee = self.get_object()
        attendee.status = models.Attendee.STATUS_CHOICES.CONFIRMED
        attendee.save()

        serializer = self.get_serializer(attendee)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def cancel(self, request, pk=None):
        """Cancel an attendee registration"""
        attendee = self.get_object()
        attendee.status = models.Attendee.STATUS_CHOICES.CANCELLED
        attendee.save()

        serializer = self.get_serializer(attendee)
        return response.Ok(serializer.data)


class SponsorViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for Sponsor model"""

    queryset = models.Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'contact_name']
    ordering_fields = ['name', 'tier', 'display_order', 'created_at']
    filterset_fields = ['event', 'tier']

    def get_queryset(self):
        return models.Sponsor.objects.select_related('event')
