# Third Party Stuff
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from extended_choices import Choices

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class RecurringPost(TimeStampedUUIDModel):
    """Model for scheduling recurring posts"""

    FREQUENCY_CHOICES = Choices(
        ('DAILY', 'daily', _('Daily')),
        ('WEEKLY', 'weekly', _('Weekly')),
        ('BIWEEKLY', 'biweekly', _('Bi-weekly')),
        ('MONTHLY', 'monthly', _('Monthly')),
        ('CUSTOM', 'custom', _('Custom')),
    )

    STATUS_CHOICES = Choices(
        ('ACTIVE', 'active', _('Active')),
        ('PAUSED', 'paused', _('Paused')),
        ('COMPLETED', 'completed', _('Completed')),
    )

    # Content
    posted_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 verbose_name=_('Posted by'))
    text = models.TextField(_('Content Text'))
    image = models.ImageField(_('Image'), upload_to='recurring_posts/', null=True, blank=True)
    video = models.FileField(_('Video'), upload_to='recurring_posts_videos/', null=True, blank=True)

    # Platforms
    posted_at = models.CharField(
        _('Posted at platform'),
        max_length=10,
        null=True,
        blank=True,
        choices=[
            ('fb', 'Facebook'),
            ('twitter', 'Twitter'),
            ('linkedin', 'Linkedin'),
            ('instagram', 'Instagram'),
            ('threads', 'Threads'),
        ]
    )
    platforms = models.JSONField(
        _('Platforms'),
        default=list,
        blank=True,
        help_text='List of platforms for multi-platform posting'
    )

    # Scheduling
    frequency = models.CharField(_('Frequency'), max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateTimeField(_('Start Date'))
    end_date = models.DateTimeField(_('End Date'), null=True, blank=True,
                                   help_text='Leave empty for indefinite')
    time_of_day = models.TimeField(_('Time of Day'),
                                   help_text='What time to post each day')

    # For weekly recurring
    weekdays = models.JSONField(
        _('Weekdays'),
        default=list,
        blank=True,
        help_text='List of weekday numbers (0=Monday, 6=Sunday) for weekly posts'
    )

    # For monthly recurring
    day_of_month = models.PositiveIntegerField(
        _('Day of Month'),
        null=True,
        blank=True,
        help_text='Day of month (1-31) for monthly posts'
    )

    # Custom interval (in days)
    custom_interval_days = models.PositiveIntegerField(
        _('Custom Interval (days)'),
        null=True,
        blank=True,
        help_text='Interval in days for custom frequency'
    )

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default=STATUS_CHOICES.ACTIVE)
    last_posted_at = models.DateTimeField(_('Last Posted At'), null=True, blank=True)
    next_post_at = models.DateTimeField(_('Next Post At'), null=True, blank=True)
    total_posts_created = models.PositiveIntegerField(_('Total Posts Created'), default=0)

    class Meta:
        verbose_name = _('Recurring Post')
        verbose_name_plural = _('Recurring Posts')
        db_table = 'recurring_posts'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.text[:50]} - {self.get_frequency_display()}'

    def calculate_next_post_time(self):
        """Calculate when this should be posted next"""
        from datetime import timedelta, datetime

        if self.status != self.STATUS_CHOICES.ACTIVE:
            return None

        base_datetime = self.last_posted_at or self.start_date
        next_time = None

        if self.frequency == self.FREQUENCY_CHOICES.DAILY:
            next_time = base_datetime + timedelta(days=1)

        elif self.frequency == self.FREQUENCY_CHOICES.WEEKLY:
            # Find next matching weekday
            current_date = base_datetime
            for _ in range(7):  # Check next 7 days
                current_date += timedelta(days=1)
                if current_date.weekday() in self.weekdays:
                    next_time = current_date
                    break

        elif self.frequency == self.FREQUENCY_CHOICES.BIWEEKLY:
            next_time = base_datetime + timedelta(days=14)

        elif self.frequency == self.FREQUENCY_CHOICES.MONTHLY:
            # Next month, same day
            if self.day_of_month:
                next_month = base_datetime.month + 1
                next_year = base_datetime.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                try:
                    next_time = datetime(next_year, next_month, self.day_of_month,
                                       self.time_of_day.hour, self.time_of_day.minute)
                except ValueError:
                    # Handle months with fewer days
                    next_time = datetime(next_year, next_month, 28,
                                       self.time_of_day.hour, self.time_of_day.minute)

        elif self.frequency == self.FREQUENCY_CHOICES.CUSTOM:
            if self.custom_interval_days:
                next_time = base_datetime + timedelta(days=self.custom_interval_days)

        # Set time of day
        if next_time:
            next_time = next_time.replace(
                hour=self.time_of_day.hour,
                minute=self.time_of_day.minute,
                second=0,
                microsecond=0
            )

        # Check if we've passed end date
        if self.end_date and next_time and next_time > self.end_date:
            self.status = self.STATUS_CHOICES.COMPLETED
            self.save()
            return None

        self.next_post_at = next_time
        self.save()
        return next_time

    def create_post_instance(self):
        """Create a Post instance from this recurring post"""
        from nexus.social_media.models import Post

        post = Post.objects.create(
            posted_by=self.posted_by,
            text=self.text,
            posted_at=self.posted_at,
            platforms=self.platforms,
            scheduled_time=self.next_post_at,
            is_approved=True,  # Auto-approve recurring posts
            is_draft=False,
        )

        if self.image:
            post.image = self.image
            post.save()

        if self.video:
            post.video = self.video
            post.save()

        # Update recurring post status
        self.last_posted_at = timezone.now()
        self.total_posts_created += 1
        self.save()

        # Calculate next post time
        self.calculate_next_post_time()

        return post
