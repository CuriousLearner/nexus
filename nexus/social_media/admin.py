# Third Party Stuff
from django.contrib import admin

# nexus Stuff
from nexus.social_media.analytics_models import PostAnalytics
from nexus.social_media.models import Post


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
            'fields': ('image', 'text', 'posted_at')
        }),
        ('Status', {
            'description': 'Status of the post in pipeline',
            'fields': (('is_approved', 'approval_time'), ('is_posted', 'posted_time'))
        })
    )
    list_display = ('posted_by', 'text', 'posted_at', 'scheduled_time', 'is_approved', 'is_posted', 'is_draft')
    list_filter = ('posted_by', 'posted_at', 'is_approved', 'is_posted', 'is_draft')
    list_select_related = True
    ordering = ('scheduled_time', )
    radio_fields = {'posted_at': admin.HORIZONTAL}
    search_fields = ['posted_by__email', 'posted_by__first_name', 'posted_by__last_name', 'text']


@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('post', 'likes', 'shares', 'comments', 'views', 'clicks', 'reach', 'engagement_rate', 'last_synced_at')
    list_filter = ('last_synced_at',)
    search_fields = ['post__text', 'post__posted_by__email']
    readonly_fields = ('engagement_rate', 'created_at', 'modified_at')
