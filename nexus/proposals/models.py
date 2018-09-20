# Third Party Stuff
from django.db import models
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class Proposal(TimeStampedUUIDModel):
    PROPOSAL_KIND = Choices(
        ('TALK', 't', _('Talk')),
        ('DEV_SPRINT', 'd', _('Dev Sprint')),
        ('WORKSHOP', 'w', _('Workshop'))
    )

    LEVELS_CHOICES = Choices(
        ('BEGINNER', 'b', _('Beginner')),
        ('INTERMEDIATE', 'i', _('Intermediate')),
        ('ADVANCED', 'a', _('Advanced'))
    )

    STATUS_CHOICES = Choices(
        ('RETRACTED', 'r', _('Retracted')),
        ('ACCEPTED', 'a', _('Accepted')),
        ('UNACCEPTED', 'u', _('Unaccpted')),
        ('SUBMITTED', 's', _('Submitted'))
    )

    title = models.CharField(_('Title'), max_length=120, null=False, blank=False)
    speaker = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('Speaker'),
                                null=False, blank=False)
    kind = models.CharField(_('Kind'), choices=PROPOSAL_KIND, max_length=10, null=False, blank=False)
    level = models.CharField(_('Content Level'), choices=LEVELS_CHOICES, max_length=12, null=False, blank=False)
    duration = models.DurationField(_('Duration'), null=False, blank=False)
    abstract = models.TextField(verbose_name=_('Abstract'), null=False, blank=False)
    description = models.TextField(verbose_name=_('Description'), null=False, blank=False)
    approved_at = models.DateTimeField(_('Approved at'), default=None, null=True, blank=True)
    status = models.CharField(_('Status'), default=STATUS_CHOICES.SUBMITTED, choices=STATUS_CHOICES,
                              max_length=10, null=False, blank=False)
    submitted_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _('Proposal')
        verbose_name_plural = _('Proposals')
        ordering = ['-submitted_at']
        db_table = "Proposals"

    def __str__(self):
        return self.title
