# Third Party Stuff
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class ReviewCriteria(TimeStampedUUIDModel):
    """Model to define review criteria for proposals"""

    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    weight = models.DecimalField(_('Weight'), max_digits=5, decimal_places=2, default=1.0,
                                 help_text='Weight of this criteria in overall score (e.g., 1.0, 1.5, 2.0)')
    max_score = models.PositiveIntegerField(_('Max Score'), default=5,
                                           help_text='Maximum score for this criteria')
    is_active = models.BooleanField(_('Is Active'), default=True)
    order = models.PositiveIntegerField(_('Order'), default=0,
                                       help_text='Display order')

    class Meta:
        verbose_name = _('Review Criteria')
        verbose_name_plural = _('Review Criteria')
        db_table = 'review_criteria'
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} (weight: {self.weight})'


class ProposalScore(TimeStampedUUIDModel):
    """Model to store scores for each review criteria"""

    review = models.ForeignKey('proposals.ProposalReview', on_delete=models.CASCADE,
                              related_name='scores', verbose_name=_('Review'))
    criteria = models.ForeignKey(ReviewCriteria, on_delete=models.PROTECT,
                                related_name='scores', verbose_name=_('Criteria'))
    score = models.PositiveIntegerField(_('Score'),
                                       validators=[MinValueValidator(0), MaxValueValidator(10)])
    notes = models.TextField(_('Notes'), blank=True,
                            help_text='Optional notes about this score')

    class Meta:
        verbose_name = _('Proposal Score')
        verbose_name_plural = _('Proposal Scores')
        db_table = 'proposal_scores'
        unique_together = [['review', 'criteria']]
        ordering = ['criteria__order']

    def __str__(self):
        return f'{self.review.proposal.title} - {self.criteria.name}: {self.score}'

    def weighted_score(self):
        """Calculate weighted score based on criteria weight"""
        return float(self.score) * float(self.criteria.weight)


class ProposalOverallScore(TimeStampedUUIDModel):
    """Model to store aggregated scores for proposals"""

    proposal = models.OneToOneField('proposals.Proposal', on_delete=models.CASCADE,
                                    related_name='overall_score', verbose_name=_('Proposal'))
    average_score = models.DecimalField(_('Average Score'), max_digits=5, decimal_places=2,
                                       default=0.0)
    weighted_average = models.DecimalField(_('Weighted Average'), max_digits=5, decimal_places=2,
                                          default=0.0)
    total_reviews = models.PositiveIntegerField(_('Total Reviews'), default=0)
    last_calculated_at = models.DateTimeField(_('Last Calculated At'), auto_now=True)

    class Meta:
        verbose_name = _('Proposal Overall Score')
        verbose_name_plural = _('Proposal Overall Scores')
        db_table = 'proposal_overall_scores'
        ordering = ['-weighted_average']

    def __str__(self):
        return f'{self.proposal.title} - {self.weighted_average}'

    def recalculate_scores(self):
        """Recalculate average scores based on all reviews"""
        from django.db.models import Avg, Count
        from nexus.proposals.reviewer_models import ProposalReview

        # Get all completed reviews
        reviews = ProposalReview.objects.filter(
            proposal=self.proposal,
            status=ProposalReview.STATUS_CHOICES.COMPLETED
        )

        self.total_reviews = reviews.count()

        if self.total_reviews == 0:
            self.average_score = 0
            self.weighted_average = 0
            self.save()
            return

        # Calculate average of all scores
        all_scores = ProposalScore.objects.filter(review__in=reviews)
        avg_data = all_scores.aggregate(avg=Avg('score'))
        self.average_score = avg_data['avg'] or 0

        # Calculate weighted average
        total_weighted = sum(score.weighted_score() for score in all_scores)
        total_weight = sum(float(score.criteria.weight) for score in all_scores)

        if total_weight > 0:
            self.weighted_average = total_weighted / total_weight
        else:
            self.weighted_average = 0

        self.save()
