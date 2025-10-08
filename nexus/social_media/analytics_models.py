# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class PostAnalytics(TimeStampedUUIDModel):
    """Post analytics model to track engagement metrics"""

    post = models.OneToOneField('social_media.Post', on_delete=models.CASCADE,
                                 related_name='analytics', verbose_name=_('Post'))
    likes = models.PositiveIntegerField(_('Likes'), default=0)
    shares = models.PositiveIntegerField(_('Shares'), default=0)
    comments = models.PositiveIntegerField(_('Comments'), default=0)
    views = models.PositiveIntegerField(_('Views'), default=0)
    clicks = models.PositiveIntegerField(_('Clicks'), default=0)
    reach = models.PositiveIntegerField(_('Reach'), default=0,
                                        help_text='Number of unique users who saw the post')
    engagement_rate = models.DecimalField(_('Engagement Rate'), max_digits=5, decimal_places=2,
                                          default=0.0, help_text='Percentage of engagement')
    last_synced_at = models.DateTimeField(_('Last Synced At'), null=True, blank=True,
                                          help_text='Last time analytics were synced from platform')

    class Meta:
        verbose_name = _('Post Analytics')
        verbose_name_plural = _('Post Analytics')
        db_table = 'post_analytics'

    def __str__(self):
        return f'Analytics for {self.post.id}'

    def calculate_engagement_rate(self):
        """Calculate engagement rate based on interactions and reach"""
        if self.reach > 0:
            total_engagement = self.likes + self.shares + self.comments + self.clicks
            self.engagement_rate = (total_engagement / self.reach) * 100
            self.save()
        return self.engagement_rate
