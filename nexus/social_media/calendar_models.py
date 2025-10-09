# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class ContentCalendar(TimeStampedUUIDModel):
    """Model to organize content calendar"""

    name = models.CharField(_('Calendar Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Date range
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'), null=True, blank=True)

    # Team
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE,
                             related_name='owned_calendars', verbose_name=_('Owner'))
    team_members = models.ManyToManyField('users.User', related_name='calendars',
                                         blank=True, verbose_name=_('Team Members'))

    # Settings
    default_platforms = models.JSONField(_('Default Platforms'), default=list, blank=True)
    color_code = models.CharField(_('Color Code'), max_length=7, default='#3498db',
                                 help_text='Hex color for calendar display')
    is_active = models.BooleanField(_('Is Active'), default=True)

    class Meta:
        verbose_name = _('Content Calendar')
        verbose_name_plural = _('Content Calendars')
        db_table = 'content_calendars'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CalendarEvent(TimeStampedUUIDModel):
    """Model for calendar events (posts, campaigns, milestones)"""

    EVENT_TYPE_CHOICES = [
        ('post', 'Post'),
        ('campaign', 'Campaign'),
        ('milestone', 'Milestone'),
        ('meeting', 'Meeting'),
        ('deadline', 'Deadline'),
    ]

    calendar = models.ForeignKey(ContentCalendar, on_delete=models.CASCADE,
                                related_name='events', verbose_name=_('Calendar'))
    event_type = models.CharField(_('Event Type'), max_length=20, choices=EVENT_TYPE_CHOICES)

    # Content
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Timing
    start_datetime = models.DateTimeField(_('Start Date/Time'))
    end_datetime = models.DateTimeField(_('End Date/Time'), null=True, blank=True)
    all_day = models.BooleanField(_('All Day Event'), default=False)

    # Relations
    post = models.ForeignKey('social_media.Post', on_delete=models.SET_NULL,
                            null=True, blank=True, related_name='calendar_events',
                            verbose_name=_('Related Post'))

    # Display
    color = models.CharField(_('Color'), max_length=7, blank=True,
                            help_text='Override calendar color')

    # Reminders
    reminder_sent = models.BooleanField(_('Reminder Sent'), default=False)

    class Meta:
        verbose_name = _('Calendar Event')
        verbose_name_plural = _('Calendar Events')
        db_table = 'calendar_events'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['calendar', 'start_datetime']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f'{self.title} - {self.start_datetime.date()}'


class Campaign(TimeStampedUUIDModel):
    """Model for marketing campaigns"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(_('Campaign Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Timing
    start_date = models.DateTimeField(_('Start Date'))
    end_date = models.DateTimeField(_('End Date'), null=True, blank=True)

    # Budget & Goals
    budget = models.DecimalField(_('Budget'), max_digits=10, decimal_places=2,
                                null=True, blank=True)
    currency = models.CharField(_('Currency'), max_length=3, default='USD')

    target_reach = models.PositiveIntegerField(_('Target Reach'), null=True, blank=True)
    target_engagement = models.PositiveIntegerField(_('Target Engagement'), null=True, blank=True)
    target_conversions = models.PositiveIntegerField(_('Target Conversions'), null=True, blank=True)

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='draft')

    # Team
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  related_name='created_campaigns', verbose_name=_('Created By'))
    team_members = models.ManyToManyField('users.User', related_name='campaigns',
                                         blank=True, verbose_name=_('Team Members'))

    # Platforms
    platforms = models.JSONField(_('Target Platforms'), default=list)

    # Tracking
    utm_campaign = models.CharField(_('UTM Campaign'), max_length=100, blank=True)
    tracking_urls = models.JSONField(_('Tracking URLs'), default=dict, blank=True)

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        db_table = 'campaigns'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def get_total_spend(self):
        """Calculate total spend from related posts"""
        # This would integrate with ad spend tracking
        return 0

    def get_roi(self):
        """Calculate ROI for campaign"""
        if not self.budget or self.budget == 0:
            return 0
        # ROI calculation would use conversion tracking
        return 0


class CampaignPost(TimeStampedUUIDModel):
    """Many-to-many relationship between campaigns and posts"""

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE,
                                related_name='campaign_posts', verbose_name=_('Campaign'))
    post = models.ForeignKey('social_media.Post', on_delete=models.CASCADE,
                            related_name='campaigns', verbose_name=_('Post'))

    # Post-specific metrics for this campaign
    spend = models.DecimalField(_('Spend'), max_digits=10, decimal_places=2,
                               null=True, blank=True)
    conversions = models.PositiveIntegerField(_('Conversions'), default=0)
    conversion_value = models.DecimalField(_('Conversion Value'), max_digits=10,
                                          decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = _('Campaign Post')
        verbose_name_plural = _('Campaign Posts')
        db_table = 'campaign_posts'
        unique_together = [['campaign', 'post']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.campaign.name} - {self.post.text[:30]}'
