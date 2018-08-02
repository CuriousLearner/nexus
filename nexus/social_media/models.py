# Third Party Stuff
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class Post(TimeStampedUUIDModel):
    """ Post model class to provide post related field
    """
    posted_by = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('Posted by'))
    posted_at = models.CharField(
        _('Posted at platform'),
        choices=(('fb', 'Facebook'),
                 ('twitter', 'Twitter'),
                 ('linkedin', 'Linkedin')),
        max_length=10)
    scheduled_time = models.DateTimeField(_('Scheduled at'), null=True)
    approval_time = models.DateTimeField(_('Approved at'), null=True)
    posted_time = models.DateTimeField(_('Posted at'), null=True)
    image = models.ImageField(_('Content Image'), blank=True)
    text = models.TextField(_('Content Text'), blank=True, null=True)
    is_approved = models.BooleanField(
        _('Is post approved'), default=False,
        help_text='is the post approved by Nexus administrator?')
    is_posted = models.BooleanField(
        _('Is posted'), default=False,
        help_text='is the post published?')

    class Meta:
        ordering = ['-scheduled_time']
