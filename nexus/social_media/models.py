# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# nexus Stuff
# Nexus Stuff
from nexus.base.models import ImageMixin, TimeStampedUUIDModel
from nexus.social_media.analytics_models import PostAnalytics  # noqa


class Post(ImageMixin, TimeStampedUUIDModel):
    """ Post model class to provide post related field
    """
    posted_by = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('Posted by'))
    PLATFORM_CHOICES = (
        ('fb', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'Linkedin'),
        ('instagram', 'Instagram'),
    )

    posted_at = models.CharField(
        _('Posted at platform'),
        choices=PLATFORM_CHOICES,
        max_length=10,
        blank=True,
        null=True,
        help_text='Leave empty for multi-platform posting')
    platforms = models.JSONField(
        _('Platforms'),
        default=list,
        blank=True,
        help_text='List of platforms for multi-platform posting. Use when posted_at is empty.'
    )
    scheduled_time = models.DateTimeField(_('Scheduled at'), null=True, blank=True)
    approval_time = models.DateTimeField(_('Approved at'), null=True, blank=True)
    posted_time = models.DateTimeField(_('Posted at'), null=True, blank=True)
    text = models.TextField(_('Content Text'), blank=True, null=True)
    is_approved = models.BooleanField(
        _('Is post approved'), default=False,
        help_text='is the post approved by Nexus administrator?')
    is_posted = models.BooleanField(
        _('Is posted'), default=False,
        help_text='is the post published?')
    is_draft = models.BooleanField(
        _('Is draft'), default=False,
        help_text='is the post saved as draft?')

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-scheduled_time']
        db_table = "posts"

    def __str__(self):
        return str(self.id)
