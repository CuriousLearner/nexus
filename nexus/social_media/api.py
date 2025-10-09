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
