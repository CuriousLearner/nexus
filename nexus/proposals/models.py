# Third Party Stuff
from django.db import models
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class Proposal(TimeStampedUUIDModel):
    LEVELS_CHOICES = Choices(
        ('BEGINNER', 'beginner', _('Beginner')),
        ('INTERMEDIATE', 'intermediate', _('Intermediate')),
        ('ADVANCED', 'advanced', _('Advanced')),
    )

    STATUS_CHOICES = Choices(
        ('RETRACTED', 'retracted', _('Retracted')),
        ('ACCEPTED', 'accepted', _('Accepted')),
        ('UNACCEPTED', 'unaccepted', _('Unaccpted')),
        ('SUBMITTED', 'submitted', _('Submitted')),
    )

    title = models.CharField(_('Title'), max_length=120, null=False, blank=False)
    speaker = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('Speaker'),
                                null=False, blank=False)
    kind = models.ForeignKey('ProposalKind', on_delete=models.CASCADE, verbose_name=_('Kind'), null=False, blank=False)
    level = models.CharField(_('Content Level'), choices=LEVELS_CHOICES, max_length=12, null=False, blank=False)
    duration = models.DurationField(_('Duration'), null=False, blank=False)
    abstract = models.TextField(verbose_name=_('Abstract'), null=False, blank=False)
    description = models.TextField(verbose_name=_('Description'), null=False, blank=False)
    accepted_at = models.DateTimeField(_('Accepted at'), default=None, null=True, blank=True)
    status = models.CharField(_('Status'), default=STATUS_CHOICES.SUBMITTED, choices=STATUS_CHOICES,
                              max_length=10, null=False, blank=False)
    submitted_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _('Proposal')
        verbose_name_plural = _('Proposals')
        db_table = "proposals"

    def __str__(self):
        return self.title


class ProposalKind(models.Model):
    kind = models.CharField(_('Kind'), max_length=10, null=False, blank=False)

    def __str__(self):
        return self.kind

    class Meta:
        verbose_name = _('Proposal kind')
        verbose_name_plural = _('Proposal kinds')
        db_table = "proposal_details"
