# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class Dashboard(TimeStampedUUIDModel):
    """Custom analytics dashboard"""

    name = models.CharField(_('Dashboard Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Ownership
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE,
                             related_name='dashboards', verbose_name=_('Owner'))
    is_public = models.BooleanField(_('Is Public'), default=False,
                                   help_text='Allow other users to view')
    shared_with = models.ManyToManyField('users.User', related_name='shared_dashboards',
                                        blank=True, verbose_name=_('Shared With'))

    # Layout
    layout_config = models.JSONField(_('Layout Config'), default=dict,
                                    help_text='Dashboard layout configuration')

    # Settings
    refresh_interval = models.PositiveIntegerField(_('Refresh Interval (seconds)'), default=300)
    date_range_default = models.CharField(_('Default Date Range'), max_length=20,
                                         choices=[
                                             ('7d', 'Last 7 Days'),
                                             ('30d', 'Last 30 Days'),
                                             ('90d', 'Last 90 Days'),
                                             ('custom', 'Custom'),
                                         ], default='30d')

    # Usage
    view_count = models.PositiveIntegerField(_('View Count'), default=0)
    last_viewed_at = models.DateTimeField(_('Last Viewed At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboards')
        db_table = 'dashboards'
        ordering = ['-last_viewed_at', '-created_at']

    def __str__(self):
        return self.name


class DashboardWidget(TimeStampedUUIDModel):
    """Widgets that make up a dashboard"""

    WIDGET_TYPE_CHOICES = [
        ('metric', 'Metric Card'),
        ('line_chart', 'Line Chart'),
        ('bar_chart', 'Bar Chart'),
        ('pie_chart', 'Pie Chart'),
        ('table', 'Data Table'),
        ('map', 'Geographic Map'),
        ('funnel', 'Funnel Chart'),
        ('gauge', 'Gauge'),
        ('leaderboard', 'Leaderboard'),
    ]

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE,
                                 related_name='widgets', verbose_name=_('Dashboard'))

    # Widget config
    widget_type = models.CharField(_('Widget Type'), max_length=20, choices=WIDGET_TYPE_CHOICES)
    title = models.CharField(_('Title'), max_length=200)
    subtitle = models.CharField(_('Subtitle'), max_length=200, blank=True)

    # Data source
    metric = models.CharField(_('Metric'), max_length=100,
                             help_text='e.g., total_posts, engagement_rate, followers')
    data_filters = models.JSONField(_('Data Filters'), default=dict,
                                   help_text='Filters to apply to data')

    # Layout
    position_x = models.PositiveIntegerField(_('Position X'), default=0)
    position_y = models.PositiveIntegerField(_('Position Y'), default=0)
    width = models.PositiveIntegerField(_('Width'), default=4)
    height = models.PositiveIntegerField(_('Height'), default=3)

    # Appearance
    color_scheme = models.CharField(_('Color Scheme'), max_length=50, default='default')
    display_config = models.JSONField(_('Display Config'), default=dict,
                                     help_text='Widget-specific display settings')

    class Meta:
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgets')
        db_table = 'dashboard_widgets'
        ordering = ['dashboard', 'position_y', 'position_x']

    def __str__(self):
        return f'{self.dashboard.name} - {self.title}'


class ScheduledReport(TimeStampedUUIDModel):
    """Model for scheduled report generation"""

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ]

    name = models.CharField(_('Report Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Schedule
    frequency = models.CharField(_('Frequency'), max_length=20, choices=FREQUENCY_CHOICES)
    day_of_week = models.PositiveIntegerField(_('Day of Week'), null=True, blank=True,
                                             help_text='0=Monday, 6=Sunday (for weekly reports)')
    day_of_month = models.PositiveIntegerField(_('Day of Month'), null=True, blank=True,
                                              help_text='1-31 (for monthly reports)')
    time_of_day = models.TimeField(_('Time of Day'))

    # Content
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE,
                                 null=True, blank=True,
                                 related_name='scheduled_reports',
                                 verbose_name=_('Dashboard'))
    report_format = models.CharField(_('Format'), max_length=20, choices=FORMAT_CHOICES)
    include_charts = models.BooleanField(_('Include Charts'), default=True)

    # Recipients
    recipients = models.ManyToManyField('users.User', related_name='scheduled_reports',
                                       verbose_name=_('Recipients'))
    additional_emails = models.JSONField(_('Additional Emails'), default=list, blank=True)

    # Status
    is_active = models.BooleanField(_('Is Active'), default=True)
    last_sent_at = models.DateTimeField(_('Last Sent At'), null=True, blank=True)
    next_send_at = models.DateTimeField(_('Next Send At'), null=True, blank=True)

    # Team
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  related_name='created_reports',
                                  verbose_name=_('Created By'))

    class Meta:
        verbose_name = _('Scheduled Report')
        verbose_name_plural = _('Scheduled Reports')
        db_table = 'scheduled_reports'
        ordering = ['next_send_at']

    def __str__(self):
        return f'{self.name} - {self.get_frequency_display()}'


class ReportSnapshot(TimeStampedUUIDModel):
    """Store generated report snapshots"""

    scheduled_report = models.ForeignKey(ScheduledReport, on_delete=models.CASCADE,
                                        null=True, blank=True,
                                        related_name='snapshots',
                                        verbose_name=_('Scheduled Report'))
    dashboard = models.ForeignKey(Dashboard, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 verbose_name=_('Dashboard'))

    # Report details
    report_name = models.CharField(_('Report Name'), max_length=200)
    report_format = models.CharField(_('Format'), max_length=20)

    # Date range covered
    date_from = models.DateField(_('Date From'))
    date_to = models.DateField(_('Date To'))

    # File
    file = models.FileField(_('Report File'), upload_to='reports/')
    file_size = models.PositiveIntegerField(_('File Size (bytes)'), default=0)

    # Metadata
    generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                    null=True, verbose_name=_('Generated By'))
    generation_time_seconds = models.FloatField(_('Generation Time (seconds)'), default=0)

    class Meta:
        verbose_name = _('Report Snapshot')
        verbose_name_plural = _('Report Snapshots')
        db_table = 'report_snapshots'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.report_name} - {self.created_at.date()}'
