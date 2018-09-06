from django.db import models
from django.utils.traslation import ugettext_lazy as _
from extended_choices import choices


class Proposal(TimeStampedUUIDModel):
    PROPOSAL_KIND = choices(
        ('talk', 't', _('Talk')),
        ('dev_sprint', 'd', _('Dev Sprint')),
        ('workshop', 'w', _('Workshop'))
    )

    LEVELS_CHOICES = choices(
        ('beginner', 'b', _('Beginner')),
        ('intermediate', 'i', _('Intermediate')),
        ('advanced', 'a', _('Advanced'))
    )

    STATUS_CHOICES = choices(
        ('retracted', 'r', _('Retracted')),
        ('accepted', 'i', _('Accepted')),
        ('unaccepted', 'u', _('Unaccpted')),
        ('submitted', 's', _('Submitted'))
    )

    title = models.CharField(_('Title'), max_length=120, null=False, blank=False)
    speaker = models.ForeignKey('users.User', verbose_name=_('Speaker'), null=False, blank=False)
    kind = models.CharField(_('Kind'), choices=PROPOSAL_KIND, max_length=10, null=False, blank=False)
    level = models.CharField(_('Content Level'), choices=LEVELS_CHOICES, max_length=12, null=False, blank=False)
    duration = models.TimeField(_('Duration'), null=False, blank=False)
    abstract = models.TextField(verbose_name=_('Abstract'), null=False, blank=False)
    description = models.TextField(verbose_name=_('Description'), null=False, blank=False)
    approved_at = models.DateTimeField(_('Approved at'), null=False, blank=False)
    status = models.CharField(_('Status'), choices=STATUS_CHOICES, max_length=10, null=False, blank=False)

    class Meta:
        verbose_name = _('Proposal')
        verbose_name_plural = _('Proposals')
        ordering = ('-submitted_at')
        db_table = "Proposals"

    def __str__(self):
        return self.title
