# Third Party Stuff
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

# nexus Stuff
from nexus.base import response
from nexus.social_media import filters as social_filters, models, permissions, serializers


class PostViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                  mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.Post.objects.all().order_by('-scheduled_time')
    permission_classes = (IsAuthenticated, permissions.IsAdminOrAuthorOfPost)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = social_filters.PostFilter
    search_fields = ['text', 'posted_by__email', 'posted_by__first_name', 'posted_by__last_name']
    ordering_fields = ['scheduled_time', 'posted_time', 'created_at', 'approval_time']

    def get_serializer_class(self):
        if self.action in ('approve', 'unapprove'):
            return serializers.AdminPostSerializer
        return serializers.PostSerializer

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsCoreOrganizer])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_approved:
            data = {'is_approved': True, 'approval_time': timezone.now()}
            serializer = self.get_serializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Ok(serializer.data)
        else:
            serializer = self.get_serializer(instance)
            return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsCoreOrganizer])
    def unapprove(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_approved:
            return response.BadRequest({'error_message': 'Post has not been approved yet'})
        elif not instance.is_posted:
            data = {'is_approved': False, 'approval_time': None}
            serializer = self.get_serializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Ok(serializer.data)
        else:
            return response.BadRequest({'error_message': 'Can not unapprove, post has already been published'})

    @action(methods=['POST'], detail=True)
    @parser_classes((FormParser, MultiPartParser))
    def upload_image(self, request, pk=None):
        from nexus.social_media import image_optimizer

        instance = self.get_object()
        if request.FILES:
            image_file = request.FILES.get('image')

            # Optimize image for the target platform(s)
            if instance.posted_at:
                optimized = image_optimizer.optimize_image_for_platform(
                    image_file, instance.posted_at
                )
                request.FILES['image'] = optimized
            elif instance.platforms:
                # Optimize for the first platform in the list
                optimized = image_optimizer.optimize_image_for_platform(
                    image_file, instance.platforms[0]
                )
                request.FILES['image'] = optimized

            data = request.data
            serializer = self.get_serializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Ok(serializer.data)
        return response.BadRequest({'error_message': 'Image file missing from the request'})

    @action(methods=['POST'], detail=True)
    @parser_classes((FormParser, MultiPartParser))
    def delete_image(self, request, pk=None):
        instance = self.get_object()
        if not instance.image:
            return response.BadRequest({'error_message': 'Image is not present for this post'})
        instance.image.delete(save=True)
        serializer = self.get_serializer(instance)
        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=True)
    def preview(self, request, pk=None):
        """Preview post content before publishing"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def duplicate(self, request, pk=None):
        """Duplicate an existing post"""
        instance = self.get_object()
        duplicated_post = models.Post.objects.create(
            posted_by=request.user,
            posted_at=instance.posted_at,
            text=instance.text,
            scheduled_time=None,
            is_approved=False,
            is_posted=False
        )
        if instance.image:
            duplicated_post.image = instance.image
            duplicated_post.save()
        serializer = self.get_serializer(duplicated_post)
        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=False)
    def export_csv(self, request):
        """Export posts to CSV format"""
        import csv
        from django.http import HttpResponse

        queryset = self.filter_queryset(self.get_queryset())

        response_csv = HttpResponse(content_type='text/csv')
        response_csv['Content-Disposition'] = 'attachment; filename="posts_export.csv"'

        writer = csv.writer(response_csv)
        writer.writerow(['ID', 'Posted By', 'Platform', 'Text', 'Scheduled Time',
                        'Posted Time', 'Is Approved', 'Is Posted', 'Is Draft', 'Created At'])

        for post in queryset:
            writer.writerow([
                str(post.id),
                post.posted_by.email,
                post.get_posted_at_display(),
                post.text or '',
                post.scheduled_time.strftime('%Y-%m-%d %H:%M:%S') if post.scheduled_time else '',
                post.posted_time.strftime('%Y-%m-%d %H:%M:%S') if post.posted_time else '',
                post.is_approved,
                post.is_posted,
                post.is_draft,
                post.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response_csv

    @action(methods=['POST'], detail=False)
    @parser_classes((FormParser, MultiPartParser))
    def bulk_upload_csv(self, request):
        """Bulk upload posts via CSV file"""
        from nexus.social_media.bulk_scheduling import BulkScheduleCSVProcessor

        if 'file' not in request.FILES:
            return response.BadRequest({'error_message': 'No CSV file provided'})

        csv_file = request.FILES['file']

        # Validate file extension
        if not csv_file.name.endswith('.csv'):
            return response.BadRequest({'error_message': 'File must be a CSV'})

        processor = BulkScheduleCSVProcessor(csv_file, request.user)
        result = processor.process()

        if result['success']:
            return response.Ok({
                'message': 'CSV processed successfully',
                'total_rows': result['total_rows'],
                'created': result['created'],
                'errors': result['errors'],
                'results': result['results']
            })
        else:
            return response.BadRequest({
                'error_message': result.get('error', 'Failed to process CSV'),
                'created': result['created'],
                'errors': result['errors']
            })

    @action(methods=['GET'], detail=False)
    def download_csv_template(self, request):
        """Download CSV template for bulk upload"""
        from django.http import HttpResponse
        from nexus.social_media.bulk_scheduling import BulkScheduleCSVProcessor

        response_csv = HttpResponse(content_type='text/csv')
        response_csv['Content-Disposition'] = 'attachment; filename="bulk_schedule_template.csv"'
        response_csv.write(BulkScheduleCSVProcessor.generate_sample_csv())

        return response_csv

    @action(methods=['GET'], detail=True)
    def hashtag_suggestions(self, request, pk=None):
        """Get hashtag suggestions for a post"""
        from nexus.social_media.hashtag_analytics import get_hashtag_suggestions

        instance = self.get_object()
        suggestions = get_hashtag_suggestions(instance.text, limit=10)

        return response.Ok({
            'suggestions': [f'#{tag}' for tag in suggestions]
        })


class HashtagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """ViewSet for hashtag analytics"""
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tag', 'category']
    ordering_fields = ['total_uses', 'total_posts', 'total_engagements', 'last_used_at']

    def get_queryset(self):
        from nexus.social_media.hashtag_analytics import Hashtag
        return Hashtag.objects.filter(is_banned=False)

    def get_serializer_class(self):
        from rest_framework import serializers
        from nexus.social_media.hashtag_analytics import Hashtag

        class HashtagSerializer(serializers.ModelSerializer):
            engagement_rate = serializers.SerializerMethodField()
            trending_score = serializers.SerializerMethodField()

            class Meta:
                model = Hashtag
                fields = ['id', 'tag', 'total_uses', 'total_posts', 'first_used_at',
                         'last_used_at', 'total_impressions', 'total_engagements',
                         'total_clicks', 'category', 'is_trending', 'engagement_rate',
                         'trending_score']

            def get_engagement_rate(self, obj):
                return round(obj.get_engagement_rate(), 2)

            def get_trending_score(self, obj):
                return round(obj.get_trending_score(), 2)

        return HashtagSerializer

    @action(methods=['GET'], detail=False)
    def trending(self, request):
        """Get trending hashtags"""
        from nexus.social_media.hashtag_analytics import get_trending_hashtags

        days = int(request.query_params.get('days', 7))
        limit = int(request.query_params.get('limit', 10))

        trending = get_trending_hashtags(limit=limit, days=days)
        serializer = self.get_serializer(trending, many=True)

        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=True)
    def performance(self, request, pk=None):
        """Get performance history for a hashtag"""
        from nexus.social_media.hashtag_analytics import HashtagPerformanceSnapshot

        hashtag = self.get_object()
        days = int(request.query_params.get('days', 30))

        cutoff_date = timezone.now().date() - timezone.timedelta(days=days)
        snapshots = HashtagPerformanceSnapshot.objects.filter(
            hashtag=hashtag,
            snapshot_date__gte=cutoff_date
        ).order_by('snapshot_date')

        data = {
            'hashtag': f'#{hashtag.tag}',
            'performance': [
                {
                    'date': snapshot.snapshot_date.isoformat(),
                    'uses': snapshot.daily_uses,
                    'posts': snapshot.daily_posts,
                    'impressions': snapshot.daily_impressions,
                    'engagements': snapshot.daily_engagements,
                    'clicks': snapshot.daily_clicks,
                    'trending_rank': snapshot.trending_rank
                }
                for snapshot in snapshots
            ]
        }

        return response.Ok(data)


class ContentCalendarViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                             mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for content calendars"""
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        from nexus.social_media.calendar_models import ContentCalendar
        # Users can see calendars they own or are members of
        return ContentCalendar.objects.filter(
            models.Q(owner=self.request.user) | models.Q(team_members=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        from rest_framework import serializers
        from nexus.social_media.calendar_models import ContentCalendar

        class ContentCalendarSerializer(serializers.ModelSerializer):
            owner_email = serializers.EmailField(source='owner.email', read_only=True)
            team_member_emails = serializers.SerializerMethodField()

            class Meta:
                model = ContentCalendar
                fields = ['id', 'name', 'description', 'start_date', 'end_date',
                         'owner', 'owner_email', 'team_members', 'team_member_emails',
                         'default_platforms', 'color_code', 'is_active', 'created_at']
                read_only_fields = ['created_at']

            def get_team_member_emails(self, obj):
                return [member.email for member in obj.team_members.all()]

        return ContentCalendarSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=['GET'], detail=True)
    def events(self, request, pk=None):
        """Get all events for a calendar"""
        from nexus.social_media.calendar_models import CalendarEvent
        from rest_framework import serializers

        calendar = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        events = CalendarEvent.objects.filter(calendar=calendar)

        if start_date:
            events = events.filter(start_datetime__gte=start_date)
        if end_date:
            events = events.filter(start_datetime__lte=end_date)

        class CalendarEventSerializer(serializers.ModelSerializer):
            post_text = serializers.CharField(source='post.text', read_only=True)

            class Meta:
                model = CalendarEvent
                fields = ['id', 'event_type', 'title', 'description', 'start_datetime',
                         'end_datetime', 'all_day', 'post', 'post_text', 'color', 'reminder_sent']

        serializer = CalendarEventSerializer(events, many=True)
        return response.Ok(serializer.data)

    @action(methods=['GET'], detail=False)
    def calendar_view(self, request):
        """Get calendar view data for all calendars user has access to"""
        from nexus.social_media.calendar_models import CalendarEvent
        from django.db.models import Q

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Get all calendars user has access to
        calendars = self.get_queryset()

        # Get events from these calendars
        events = CalendarEvent.objects.filter(calendar__in=calendars)

        if start_date:
            events = events.filter(start_datetime__gte=start_date)
        if end_date:
            events = events.filter(start_datetime__lte=end_date)

        # Group events by date
        calendar_data = {}
        for event in events:
            date_key = event.start_datetime.date().isoformat()
            if date_key not in calendar_data:
                calendar_data[date_key] = []

            calendar_data[date_key].append({
                'id': str(event.id),
                'calendar_name': event.calendar.name,
                'event_type': event.event_type,
                'title': event.title,
                'start_datetime': event.start_datetime.isoformat(),
                'end_datetime': event.end_datetime.isoformat() if event.end_datetime else None,
                'color': event.color or event.calendar.color_code,
                'post_id': str(event.post.id) if event.post else None
            })

        return response.Ok(calendar_data)


class CampaignViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for marketing campaigns"""
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        from nexus.social_media.calendar_models import Campaign
        return Campaign.objects.filter(
            models.Q(created_by=self.request.user) | models.Q(team_members=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        from rest_framework import serializers
        from nexus.social_media.calendar_models import Campaign

        class CampaignSerializer(serializers.ModelSerializer):
            created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
            total_posts = serializers.SerializerMethodField()
            roi = serializers.SerializerMethodField()

            class Meta:
                model = Campaign
                fields = ['id', 'name', 'description', 'start_date', 'end_date',
                         'budget', 'currency', 'target_reach', 'target_engagement',
                         'target_conversions', 'status', 'created_by', 'created_by_email',
                         'team_members', 'platforms', 'utm_campaign', 'total_posts', 'roi']
                read_only_fields = ['created_at']

            def get_total_posts(self, obj):
                return obj.campaign_posts.count()

            def get_roi(self, obj):
                return obj.get_roi()

        return CampaignSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(methods=['POST'], detail=True)
    def add_post(self, request, pk=None):
        """Add a post to this campaign"""
        from nexus.social_media.calendar_models import CampaignPost

        campaign = self.get_object()
        post_id = request.data.get('post_id')

        if not post_id:
            return response.BadRequest({'error_message': 'post_id is required'})

        try:
            post = models.Post.objects.get(id=post_id)
        except models.Post.DoesNotExist:
            return response.BadRequest({'error_message': 'Post not found'})

        campaign_post, created = CampaignPost.objects.get_or_create(
            campaign=campaign,
            post=post
        )

        if created:
            return response.Ok({'message': 'Post added to campaign'})
        else:
            return response.BadRequest({'error_message': 'Post already in campaign'})

    @action(methods=['GET'], detail=True)
    def performance(self, request, pk=None):
        """Get campaign performance metrics"""
        campaign = self.get_object()

        # Aggregate metrics from all posts in campaign
        campaign_posts = campaign.campaign_posts.all()
        total_spend = sum(cp.spend or 0 for cp in campaign_posts)
        total_conversions = sum(cp.conversions for cp in campaign_posts)
        total_conversion_value = sum(cp.conversion_value or 0 for cp in campaign_posts)

        # Get analytics from posts
        total_reach = 0
        total_engagement = 0
        total_impressions = 0

        for cp in campaign_posts:
            if hasattr(cp.post, 'analytics'):
                analytics = cp.post.analytics
                total_reach += analytics.reach
                total_engagement += (analytics.likes + analytics.shares + analytics.comments)
                total_impressions += analytics.views

        data = {
            'campaign': campaign.name,
            'status': campaign.status,
            'budget': float(campaign.budget) if campaign.budget else 0,
            'total_spend': float(total_spend),
            'total_posts': campaign_posts.count(),
            'total_impressions': total_impressions,
            'total_reach': total_reach,
            'total_engagement': total_engagement,
            'total_conversions': total_conversions,
            'total_conversion_value': float(total_conversion_value),
            'roi': campaign.get_roi(),
            'target_reach': campaign.target_reach,
            'target_engagement': campaign.target_engagement,
            'target_conversions': campaign.target_conversions
        }

        return response.Ok(data)
