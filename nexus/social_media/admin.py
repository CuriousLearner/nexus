# Third Party Stuff
from django.contrib import admin

# nexus Stuff
from nexus.social_media.analytics_models import PostAnalytics
from nexus.social_media.hashtag_analytics import Hashtag, HashtagPerformanceSnapshot, PostHashtag
from nexus.social_media.models import Post, PlatformSchedule
from nexus.social_media.queue_models import PostQueue, SchedulingRule
from nexus.social_media.recurring_models import RecurringPost
from nexus.social_media.template_models import PostTemplate, TemplateVariable


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Author', {
            'description': 'Information about the person authoring the post',
            'fields': ('posted_by', )
        }),
        ('Timing', {
            'description': 'Timing details about the Post',
            'fields': ('scheduled_time', )
        }),
        ('Content', {
            'description': 'Actual content to be posted',
            'fields': ('image', 'video', 'text', 'posted_at', 'platforms')
        }),
        ('Status', {
            'description': 'Status of the post in pipeline',
            'fields': (('is_approved', 'approval_time'), ('is_posted', 'posted_time'), 'is_draft')
        })
    )
    list_display = ('posted_by', 'text', 'posted_at', 'scheduled_time', 'is_approved', 'is_posted', 'is_draft')
    list_filter = ('posted_by', 'posted_at', 'is_approved', 'is_posted', 'is_draft')
    list_select_related = True
    ordering = ('scheduled_time', )
    search_fields = ['posted_by__email', 'posted_by__first_name', 'posted_by__last_name', 'text']


@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('post', 'likes', 'shares', 'comments', 'views', 'clicks', 'reach', 'engagement_rate', 'last_synced_at')
    list_filter = ('last_synced_at',)
    search_fields = ['post__text', 'post__posted_by__email']
    readonly_fields = ('engagement_rate', 'created_at', 'modified_at')


@admin.register(PlatformSchedule)
class PlatformScheduleAdmin(admin.ModelAdmin):
    list_display = ('post', 'platform', 'scheduled_time', 'is_posted', 'posted_time')
    list_filter = ('platform', 'is_posted', 'scheduled_time')
    search_fields = ['post__text']
    readonly_fields = ('posted_time',)


@admin.register(RecurringPost)
class RecurringPostAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'posted_by', 'frequency', 'status', 'next_post_at', 'total_posts_created')
    list_filter = ('frequency', 'status', 'posted_by')
    search_fields = ['text', 'posted_by__email']
    readonly_fields = ('last_posted_at', 'next_post_at', 'total_posts_created')

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Text'


@admin.register(PostTemplate)
class PostTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'category', 'times_used', 'is_public', 'created_at')
    list_filter = ('is_public', 'category', 'created_by')
    search_fields = ['name', 'description', 'text_template']
    readonly_fields = ('times_used', 'last_used_at')


class TemplateVariableInline(admin.TabularInline):
    model = TemplateVariable
    extra = 1


@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'is_required', 'default_value')
    list_filter = ('is_required', 'template')
    search_fields = ['name', 'template__name']


@admin.register(PostQueue)
class PostQueueAdmin(admin.ModelAdmin):
    list_display = ('queue_position', 'post_preview', 'priority', 'auto_schedule', 'assigned_to', 'created_at')
    list_filter = ('priority', 'auto_schedule', 'assigned_to')
    search_fields = ['post__text', 'notes']
    ordering = ('queue_position',)

    def post_preview(self, obj):
        return obj.post.text[:50]
    post_preview.short_description = 'Post'


@admin.register(SchedulingRule)
class SchedulingRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_posts_per_day', 'min_hours_between_posts', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ['name', 'description']


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'total_uses', 'total_posts', 'category', 'is_trending', 'is_banned', 'last_used_at')
    list_filter = ('is_trending', 'is_banned', 'category')
    search_fields = ['tag', 'tag_lower']
    readonly_fields = ('total_uses', 'total_posts', 'first_used_at', 'last_used_at',
                      'total_impressions', 'total_engagements', 'total_clicks')


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = ('hashtag', 'post_preview', 'platform', 'impressions', 'engagements', 'clicks')
    list_filter = ('platform', 'hashtag')
    search_fields = ['post__text', 'hashtag__tag']
    readonly_fields = ('created_at',)

    def post_preview(self, obj):
        return obj.post.text[:30]
    post_preview.short_description = 'Post'


@admin.register(HashtagPerformanceSnapshot)
class HashtagPerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ('hashtag', 'snapshot_date', 'daily_posts', 'daily_uses', 'daily_engagements', 'trending_rank')
    list_filter = ('snapshot_date', 'trending_rank')
    search_fields = ['hashtag__tag']
    readonly_fields = ('snapshot_date',)
