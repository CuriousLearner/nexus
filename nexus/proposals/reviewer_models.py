# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _
from extended_choices import Choices

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class ProposalReviewer(TimeStampedUUIDModel):
    """Model to assign reviewers to proposals"""

    proposal = models.ForeignKey('proposals.Proposal', on_delete=models.CASCADE,
                                 related_name='reviewers', verbose_name=_('Proposal'))
    reviewer = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='reviewed_proposals', verbose_name=_('Reviewer'))
    assigned_at = models.DateTimeField(_('Assigned At'), auto_now_add=True)
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                   related_name='reviewer_assignments', verbose_name=_('Assigned By'))

    class Meta:
        verbose_name = _('Proposal Reviewer')
        verbose_name_plural = _('Proposal Reviewers')
        db_table = 'proposal_reviewers'
        unique_together = [['proposal', 'reviewer']]
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.reviewer.email} reviewing {self.proposal.title}'


class ProposalReview(TimeStampedUUIDModel):
    """Model to store individual reviews for proposals"""

    STATUS_CHOICES = Choices(
        ('PENDING', 'pending', _('Pending')),
        ('COMPLETED', 'completed', _('Completed')),
    )

    RECOMMENDATION_CHOICES = Choices(
        ('STRONG_ACCEPT', 'strong_accept', _('Strong Accept')),
        ('ACCEPT', 'accept', _('Accept')),
        ('BORDERLINE', 'borderline', _('Borderline')),
        ('REJECT', 'reject', _('Reject')),
        ('STRONG_REJECT', 'strong_reject', _('Strong Reject')),
    )

    proposal = models.ForeignKey('proposals.Proposal', on_delete=models.CASCADE,
                                 related_name='reviews', verbose_name=_('Proposal'))
    reviewer = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='proposal_reviews', verbose_name=_('Reviewer'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default=STATUS_CHOICES.PENDING)
    recommendation = models.CharField(_('Recommendation'), max_length=20,
                                     choices=RECOMMENDATION_CHOICES, null=True, blank=True)

    # Review comments
    comments = models.TextField(_('Comments'), blank=True,
                               help_text='Private comments for organizers')
    feedback_for_speaker = models.TextField(_('Feedback for Speaker'), blank=True,
                                           help_text='Public feedback that will be shared with speaker')

    # Review metadata
    reviewed_at = models.DateTimeField(_('Reviewed At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Proposal Review')
        verbose_name_plural = _('Proposal Reviews')
        db_table = 'proposal_reviews'
        unique_together = [['proposal', 'reviewer']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reviewer.email} - {self.proposal.title} - {self.recommendation or "Pending"}'
