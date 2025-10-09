# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class ABTest(TimeStampedUUIDModel):
    """Model for A/B testing posts"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(_('Test Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    hypothesis = models.TextField(_('Hypothesis'),
                                  help_text='What you expect to learn from this test')

    # Test configuration
    variable_being_tested = models.CharField(_('Variable Being Tested'), max_length=100,
                                            help_text='e.g., headline, image, time, hashtags')

    # Timing
    start_date = models.DateTimeField(_('Start Date'))
    end_date = models.DateTimeField(_('End Date'), null=True, blank=True)
    duration_hours = models.PositiveIntegerField(_('Duration (hours)'), default=24)

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='draft')

    # Winner
    winning_variant = models.ForeignKey('social_media.Post', on_delete=models.SET_NULL,
                                       null=True, blank=True,
                                       related_name='won_tests',
                                       verbose_name=_('Winning Variant'))
    confidence_level = models.FloatField(_('Confidence Level'), null=True, blank=True,
                                        help_text='Statistical confidence (0-100%)')

    # Team
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  related_name='ab_tests', verbose_name=_('Created By'))

    class Meta:
        verbose_name = _('A/B Test')
        verbose_name_plural = _('A/B Tests')
        db_table = 'ab_tests'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def determine_winner(self):
        """Determine the winning variant based on performance metrics"""
        variants = self.variants.all()

        if variants.count() < 2:
            return None

        # Calculate score for each variant
        variant_scores = []
        for variant in variants:
            if hasattr(variant.post, 'analytics'):
                analytics = variant.post.analytics
                # Score based on engagement rate
                if analytics.reach > 0:
                    engagement_rate = (
                        (analytics.likes + analytics.shares + analytics.comments) / analytics.reach
                    ) * 100
                    variant_scores.append({
                        'variant': variant,
                        'score': engagement_rate,
                        'engagement': analytics.likes + analytics.shares + analytics.comments
                    })

        if not variant_scores:
            return None

        # Find best performing variant
        winner = max(variant_scores, key=lambda x: x['score'])

        self.winning_variant = winner['variant'].post
        self.status = 'completed'

        # Simple confidence calculation (would use statistical test in production)
        scores = [v['score'] for v in variant_scores]
        if len(scores) >= 2:
            winner_score = winner['score']
            runner_up = sorted(scores, reverse=True)[1]
            if runner_up > 0:
                self.confidence_level = min(
                    ((winner_score - runner_up) / runner_up) * 100,
                    99.9
                )
            else:
                self.confidence_level = 99.9

        self.save()
        return self.winning_variant


class ABTestVariant(TimeStampedUUIDModel):
    """Variants for A/B tests"""

    test = models.ForeignKey(ABTest, on_delete=models.CASCADE,
                            related_name='variants', verbose_name=_('A/B Test'))
    post = models.ForeignKey('social_media.Post', on_delete=models.CASCADE,
                            related_name='ab_test_variants', verbose_name=_('Post'))

    variant_name = models.CharField(_('Variant Name'), max_length=100,
                                   help_text='e.g., Control, Variant A, Variant B')
    is_control = models.BooleanField(_('Is Control'), default=False)

    # Audience split (percentage)
    audience_percentage = models.FloatField(_('Audience Percentage'), default=50.0,
                                           help_text='Percentage of audience that sees this variant')

    class Meta:
        verbose_name = _('A/B Test Variant')
        verbose_name_plural = _('A/B Test Variants')
        db_table = 'ab_test_variants'
        unique_together = [['test', 'variant_name']]
        ordering = ['test', 'is_control', 'variant_name']

    def __str__(self):
        return f'{self.test.name} - {self.variant_name}'


class ROITracker(TimeStampedUUIDModel):
    """Model to track ROI for posts and campaigns"""

    # What we're tracking
    post = models.OneToOneField('social_media.Post', on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='roi_tracker', verbose_name=_('Post'))
    campaign = models.ForeignKey('social_media.Campaign', on_delete=models.CASCADE,
                                null=True, blank=True,
                                related_name='roi_trackers', verbose_name=_('Campaign'))

    # Costs
    content_creation_cost = models.DecimalField(_('Content Creation Cost'), max_digits=10,
                                               decimal_places=2, default=0)
    ad_spend = models.DecimalField(_('Ad Spend'), max_digits=10, decimal_places=2, default=0)
    tool_costs = models.DecimalField(_('Tool Costs'), max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(_('Other Costs'), max_digits=10, decimal_places=2, default=0)

    # Revenue/Value
    direct_revenue = models.DecimalField(_('Direct Revenue'), max_digits=10, decimal_places=2,
                                        default=0, help_text='Revenue directly attributed')
    conversions = models.PositiveIntegerField(_('Conversions'), default=0)
    conversion_value = models.DecimalField(_('Conversion Value'), max_digits=10,
                                          decimal_places=2, default=0)

    # Attribution
    assisted_conversions = models.PositiveIntegerField(_('Assisted Conversions'), default=0,
                                                      help_text='Conversions where this contributed')

    # Metrics
    cost_per_click = models.DecimalField(_('Cost Per Click'), max_digits=10, decimal_places=2,
                                        null=True, blank=True)
    cost_per_engagement = models.DecimalField(_('Cost Per Engagement'), max_digits=10,
                                             decimal_places=2, null=True, blank=True)
    cost_per_conversion = models.DecimalField(_('Cost Per Conversion'), max_digits=10,
                                             decimal_places=2, null=True, blank=True)

    roi_percentage = models.FloatField(_('ROI Percentage'), null=True, blank=True)

    class Meta:
        verbose_name = _('ROI Tracker')
        verbose_name_plural = _('ROI Trackers')
        db_table = 'roi_trackers'
        ordering = ['-created_at']

    def __str__(self):
        if self.post:
            return f'ROI for Post: {self.post.text[:30]}'
        elif self.campaign:
            return f'ROI for Campaign: {self.campaign.name}'
        return f'ROI Tracker {self.id}'

    def calculate_total_cost(self):
        """Calculate total investment"""
        return (
            self.content_creation_cost +
            self.ad_spend +
            self.tool_costs +
            self.other_costs
        )

    def calculate_total_value(self):
        """Calculate total value generated"""
        return self.direct_revenue + self.conversion_value

    def calculate_roi(self):
        """Calculate ROI percentage"""
        total_cost = self.calculate_total_cost()
        total_value = self.calculate_total_value()

        if total_cost == 0:
            self.roi_percentage = 0
        else:
            self.roi_percentage = ((total_value - total_cost) / total_cost) * 100

        self.save()
        return self.roi_percentage

    def update_metrics(self):
        """Update calculated metrics"""
        total_cost = self.calculate_total_cost()

        # Get analytics if this is for a post
        if self.post and hasattr(self.post, 'analytics'):
            analytics = self.post.analytics

            # Cost per click
            if analytics.clicks > 0 and total_cost > 0:
                self.cost_per_click = total_cost / analytics.clicks

            # Cost per engagement
            total_engagement = analytics.likes + analytics.shares + analytics.comments
            if total_engagement > 0 and total_cost > 0:
                self.cost_per_engagement = total_cost / total_engagement

        # Cost per conversion
        if self.conversions > 0 and total_cost > 0:
            self.cost_per_conversion = total_cost / self.conversions

        # Calculate ROI
        self.calculate_roi()


class ConversionTracking(TimeStampedUUIDModel):
    """Model to track individual conversions"""

    CONVERSION_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('signup', 'Signup'),
        ('download', 'Download'),
        ('contact', 'Contact Form'),
        ('booking', 'Booking'),
        ('other', 'Other'),
    ]

    post = models.ForeignKey('social_media.Post', on_delete=models.CASCADE,
                            related_name='conversions', verbose_name=_('Post'))
    campaign = models.ForeignKey('social_media.Campaign', on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='conversions', verbose_name=_('Campaign'))

    # Conversion details
    conversion_type = models.CharField(_('Conversion Type'), max_length=20,
                                      choices=CONVERSION_TYPE_CHOICES)
    conversion_value = models.DecimalField(_('Conversion Value'), max_digits=10,
                                          decimal_places=2, default=0)
    currency = models.CharField(_('Currency'), max_length=3, default='USD')

    # Attribution
    conversion_date = models.DateTimeField(_('Conversion Date'))
    days_to_convert = models.PositiveIntegerField(_('Days to Convert'), default=0,
                                                  help_text='Days from post to conversion')

    # Tracking
    utm_source = models.CharField(_('UTM Source'), max_length=100, blank=True)
    utm_medium = models.CharField(_('UTM Medium'), max_length=100, blank=True)
    utm_campaign = models.CharField(_('UTM Campaign'), max_length=100, blank=True)
    referrer_url = models.URLField(_('Referrer URL'), max_length=500, blank=True)

    # Customer info (optional)
    customer_id = models.CharField(_('Customer ID'), max_length=100, blank=True)
    customer_email = models.EmailField(_('Customer Email'), blank=True)

    class Meta:
        verbose_name = _('Conversion Tracking')
        verbose_name_plural = _('Conversion Trackings')
        db_table = 'conversion_tracking'
        ordering = ['-conversion_date']
        indexes = [
            models.Index(fields=['post', '-conversion_date']),
            models.Index(fields=['campaign', '-conversion_date']),
            models.Index(fields=['conversion_type']),
        ]

    def __str__(self):
        return f'{self.conversion_type} - {self.conversion_value} - {self.conversion_date.date()}'
