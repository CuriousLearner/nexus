# Third Party Stuff
from django.contrib import admin

# nexus Stuff
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
    list_display = ('posted_by', 'text', 'posted_at', 'scheduled_time', 'is_approved', 'is_posted')
    list_filter = ('posted_by', 'posted_at', 'is_approved', 'is_posted')
    list_select_related = True
    ordering = ('scheduled_time', )
    radio_fields = {'posted_at': admin.HORIZONTAL}
    search_fields = ['posted_by__email', 'posted_by__first_name', 'posted_by__last_name', 'text']
