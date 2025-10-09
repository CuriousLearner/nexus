# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _
from extended_choices import Choices

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class PostQueue(TimeStampedUUIDModel):
    """Model to manage post queue/ordering"""

    post = models.OneToOneField('social_media.Post', on_delete=models.CASCADE,
                                related_name='queue_item', verbose_name=_('Post'))
    queue_position = models.PositiveIntegerField(_('Queue Position'), default=0,
                                                help_text='Lower number = higher priority')
    priority = models.CharField(
        _('Priority'),
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='normal'
    )

    # Auto-scheduling
    auto_schedule = models.BooleanField(_('Auto Schedule'), default=False,
                                       help_text='Automatically schedule when slot available')
    preferred_time_start = models.TimeField(_('Preferred Time Start'), null=True, blank=True)
    preferred_time_end = models.TimeField(_('Preferred Time End'), null=True, blank=True)

    # Metadata
    notes = models.TextField(_('Notes'), blank=True)
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='assigned_queue_items',
                                   verbose_name=_('Assigned To'))

    class Meta:
        verbose_name = _('Post Queue Item')
        verbose_name_plural = _('Post Queue Items')
        db_table = 'post_queue'
        ordering = ['queue_position', '-priority', 'created_at']

    def __str__(self):
        return f'Queue #{self.queue_position} - {self.post.text[:50]}'

    def move_up(self):
        """Move post up in queue (decrease position number)"""
        if self.queue_position > 0:
            # Swap with item above
            try:
                above_item = PostQueue.objects.get(queue_position=self.queue_position - 1)
                above_item.queue_position += 1
                above_item.save()
            except PostQueue.DoesNotExist:
                pass

            self.queue_position -= 1
            self.save()

    def move_down(self):
        """Move post down in queue (increase position number)"""
        try:
            below_item = PostQueue.objects.get(queue_position=self.queue_position + 1)
            below_item.queue_position -= 1
            below_item.save()

            self.queue_position += 1
            self.save()
        except PostQueue.DoesNotExist:
            pass

    def move_to_top(self):
        """Move post to top of queue"""
        # Shift all items down
        PostQueue.objects.filter(queue_position__lt=self.queue_position).update(
            queue_position=models.F('queue_position') + 1
        )
        self.queue_position = 0
        self.save()

    def move_to_bottom(self):
        """Move post to bottom of queue"""
        max_position = PostQueue.objects.aggregate(models.Max('queue_position'))['queue_position__max'] or 0
        self.queue_position = max_position + 1
        self.save()


class SchedulingRule(TimeStampedUUIDModel):
    """Model to define scheduling rules for auto-posting"""

    name = models.CharField(_('Rule Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Timing rules
    weekdays = models.JSONField(
        _('Weekdays'),
        default=list,
        help_text='List of weekday numbers (0=Monday, 6=Sunday)'
    )
    time_slots = models.JSONField(
        _('Time Slots'),
        default=list,
        help_text='List of time ranges like [["09:00", "10:00"], ["14:00", "15:00"]]'
    )

    # Frequency limits
    max_posts_per_day = models.PositiveIntegerField(_('Max Posts Per Day'), default=5)
    min_hours_between_posts = models.PositiveIntegerField(_('Min Hours Between Posts'), default=2)

    # Platform-specific
    platforms = models.JSONField(
        _('Platforms'),
        default=list,
        blank=True,
        help_text='Apply rule to specific platforms only'
    )

    # Status
    is_active = models.BooleanField(_('Is Active'), default=True)

    class Meta:
        verbose_name = _('Scheduling Rule')
        verbose_name_plural = _('Scheduling Rules')
        db_table = 'scheduling_rules'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_next_available_slot(self, start_from=None):
        """Find next available time slot based on this rule

        :param start_from: Start searching from this datetime
        :returns: Next available datetime or None
        """
        from datetime import datetime, timedelta
        from django.utils import timezone as tz

        if start_from is None:
            start_from = tz.now()

        # Check up to 30 days ahead
        for day_offset in range(30):
            check_date = start_from + timedelta(days=day_offset)

            # Check if weekday is allowed
            if check_date.weekday() not in self.weekdays:
                continue

            # Check each time slot
            for time_slot in self.time_slots:
                start_time_str, end_time_str = time_slot
                start_hour, start_min = map(int, start_time_str.split(':'))
                end_hour, end_min = map(int, end_time_str.split(':'))

                slot_start = check_date.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
                slot_end = check_date.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)

                # Check if slot is in the future
                if slot_start < start_from:
                    continue

                # Check if within daily limit
                from nexus.social_media.models import Post
                posts_today = Post.objects.filter(
                    scheduled_time__date=check_date.date()
                ).count()

                if posts_today >= self.max_posts_per_day:
                    break  # Try next day

                # Check min hours between posts
                recent_post = Post.objects.filter(
                    scheduled_time__gte=slot_start - timedelta(hours=self.min_hours_between_posts),
                    scheduled_time__lte=slot_start
                ).first()

                if not recent_post:
                    return slot_start

        return None
