# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class PlatformSchedule(TimeStampedUUIDModel):
    """Model to schedule posts for different platforms at different times"""

    post = models.ForeignKey('social_media.Post', on_delete=models.CASCADE,
                            related_name='platform_schedules', verbose_name=_('Post'))
    platform = models.CharField(_('Platform'), max_length=20,
                               choices=[
                                   ('fb', 'Facebook'),
                                   ('twitter', 'Twitter'),
                                   ('linkedin', 'Linkedin'),
                                   ('instagram', 'Instagram'),
                                   ('threads', 'Threads'),
                               ])
    scheduled_time = models.DateTimeField(_('Scheduled Time'))
    is_posted = models.BooleanField(_('Is Posted'), default=False)
    posted_time = models.DateTimeField(_('Posted Time'), null=True, blank=True)
    error_message = models.TextField(_('Error Message'), blank=True,
                                     help_text='Error if posting failed')

    class Meta:
        verbose_name = _('Platform Schedule')
        verbose_name_plural = _('Platform Schedules')
        db_table = 'platform_schedules'
        ordering = ['scheduled_time']
        indexes = [
            models.Index(fields=['scheduled_time', 'is_posted']),
            models.Index(fields=['platform', 'is_posted']),
        ]

    def __str__(self):
        return f'{self.post.text[:50]} - {self.platform} at {self.scheduled_time}'
