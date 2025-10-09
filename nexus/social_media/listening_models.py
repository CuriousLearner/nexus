# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class MonitoredKeyword(TimeStampedUUIDModel):
    """Model to track keywords for social listening"""

    keyword = models.CharField(_('Keyword'), max_length=200, db_index=True)
    is_active = models.BooleanField(_('Is Active'), default=True)

    # Monitoring settings
    platforms = models.JSONField(_('Platforms to Monitor'), default=list,
                                help_text='List of platforms to monitor')
    languages = models.JSONField(_('Languages'), default=list, blank=True,
                                help_text='Language codes to filter, empty = all')

    # Alert settings
    alert_threshold = models.PositiveIntegerField(_('Alert Threshold'), default=10,
                                                  help_text='Alert when mentions exceed this number per hour')
    alert_on_negative = models.BooleanField(_('Alert on Negative Sentiment'), default=True)

    # Team
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  related_name='monitored_keywords',
                                  verbose_name=_('Created By'))
    notify_users = models.ManyToManyField('users.User', related_name='keyword_alerts',
                                         blank=True, verbose_name=_('Users to Notify'))

    class Meta:
        verbose_name = _('Monitored Keyword')
        verbose_name_plural = _('Monitored Keywords')
        db_table = 'monitored_keywords'
        ordering = ['-created_at']

    def __str__(self):
        return self.keyword


class SocialMention(TimeStampedUUIDModel):
    """Model to store social media mentions found during monitoring"""

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('unknown', 'Unknown'),
    ]

    keyword = models.ForeignKey(MonitoredKeyword, on_delete=models.CASCADE,
                               related_name='mentions', verbose_name=_('Keyword'))

    # Source info
    platform = models.CharField(_('Platform'), max_length=20,
                               choices=[
                                   ('fb', 'Facebook'),
                                   ('twitter', 'Twitter'),
                                   ('linkedin', 'Linkedin'),
                                   ('instagram', 'Instagram'),
                                   ('threads', 'Threads'),
                               ])
    external_id = models.CharField(_('External ID'), max_length=200, db_index=True,
                                  help_text='ID from the platform')
    url = models.URLField(_('URL'), max_length=500)

    # Content
    text = models.TextField(_('Text'))
    author_name = models.CharField(_('Author Name'), max_length=200)
    author_username = models.CharField(_('Author Username'), max_length=200)
    author_followers = models.PositiveIntegerField(_('Author Followers'), default=0)

    # Metadata
    published_at = models.DateTimeField(_('Published At'))
    language = models.CharField(_('Language'), max_length=10, blank=True)

    # Engagement
    likes = models.PositiveIntegerField(_('Likes'), default=0)
    shares = models.PositiveIntegerField(_('Shares'), default=0)
    comments = models.PositiveIntegerField(_('Comments'), default=0)
    reach = models.PositiveIntegerField(_('Reach'), default=0)

    # Sentiment analysis
    sentiment = models.CharField(_('Sentiment'), max_length=20,
                                choices=SENTIMENT_CHOICES, default='unknown')
    sentiment_score = models.FloatField(_('Sentiment Score'), null=True, blank=True,
                                       help_text='Sentiment score from -1 to 1')

    # Status
    is_read = models.BooleanField(_('Is Read'), default=False)
    is_responded = models.BooleanField(_('Is Responded'), default=False)
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='assigned_mentions',
                                   verbose_name=_('Assigned To'))

    # Response
    response_post = models.ForeignKey('social_media.Post', on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='mention_responses',
                                     verbose_name=_('Response Post'))

    class Meta:
        verbose_name = _('Social Mention')
        verbose_name_plural = _('Social Mentions')
        db_table = 'social_mentions'
        ordering = ['-published_at']
        unique_together = [['platform', 'external_id']]
        indexes = [
            models.Index(fields=['keyword', '-published_at']),
            models.Index(fields=['sentiment']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f'{self.author_username} on {self.platform} - {self.text[:50]}'

    def analyze_sentiment(self):
        """Analyze sentiment of the mention text"""
        # This would integrate with sentiment analysis API
        # For now, simple keyword-based sentiment
        positive_words = ['great', 'awesome', 'love', 'excellent', 'good', 'amazing', 'perfect']
        negative_words = ['bad', 'terrible', 'hate', 'worst', 'awful', 'poor', 'horrible']

        text_lower = self.text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            self.sentiment = 'positive'
            self.sentiment_score = 0.5
        elif negative_count > positive_count:
            self.sentiment = 'negative'
            self.sentiment_score = -0.5
        else:
            self.sentiment = 'neutral'
            self.sentiment_score = 0.0

        self.save()


class CompetitorAccount(TimeStampedUUIDModel):
    """Model to track competitor social media accounts"""

    name = models.CharField(_('Company/Brand Name'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Social accounts
    twitter_username = models.CharField(_('Twitter Username'), max_length=100, blank=True)
    facebook_page_id = models.CharField(_('Facebook Page ID'), max_length=100, blank=True)
    linkedin_company_id = models.CharField(_('LinkedIn Company ID'), max_length=100, blank=True)
    instagram_username = models.CharField(_('Instagram Username'), max_length=100, blank=True)

    # Settings
    is_active = models.BooleanField(_('Is Active'), default=True)
    monitoring_frequency = models.CharField(_('Monitoring Frequency'), max_length=20,
                                           choices=[
                                               ('hourly', 'Hourly'),
                                               ('daily', 'Daily'),
                                               ('weekly', 'Weekly'),
                                           ], default='daily')

    # Team
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  related_name='tracked_competitors',
                                  verbose_name=_('Created By'))

    class Meta:
        verbose_name = _('Competitor Account')
        verbose_name_plural = _('Competitor Accounts')
        db_table = 'competitor_accounts'
        ordering = ['name']

    def __str__(self):
        return self.name


class CompetitorPost(TimeStampedUUIDModel):
    """Model to store competitor posts"""

    competitor = models.ForeignKey(CompetitorAccount, on_delete=models.CASCADE,
                                  related_name='posts', verbose_name=_('Competitor'))

    # Source info
    platform = models.CharField(_('Platform'), max_length=20)
    external_id = models.CharField(_('External ID'), max_length=200)
    url = models.URLField(_('URL'), max_length=500)

    # Content
    text = models.TextField(_('Text'), blank=True)
    has_image = models.BooleanField(_('Has Image'), default=False)
    has_video = models.BooleanField(_('Has Video'), default=False)
    hashtags = models.JSONField(_('Hashtags'), default=list)

    # Metadata
    published_at = models.DateTimeField(_('Published At'))

    # Engagement metrics
    likes = models.PositiveIntegerField(_('Likes'), default=0)
    shares = models.PositiveIntegerField(_('Shares'), default=0)
    comments = models.PositiveIntegerField(_('Comments'), default=0)
    views = models.PositiveIntegerField(_('Views'), default=0)

    # Analysis
    engagement_rate = models.FloatField(_('Engagement Rate'), default=0.0)
    sentiment = models.CharField(_('Sentiment'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('Competitor Post')
        verbose_name_plural = _('Competitor Posts')
        db_table = 'competitor_posts'
        ordering = ['-published_at']
        unique_together = [['competitor', 'platform', 'external_id']]
        indexes = [
            models.Index(fields=['competitor', '-published_at']),
            models.Index(fields=['-engagement_rate']),
        ]

    def __str__(self):
        return f'{self.competitor.name} - {self.published_at.date()}'

    def calculate_engagement_rate(self):
        """Calculate engagement rate for this post"""
        total_engagement = self.likes + self.shares + self.comments
        if self.views > 0:
            self.engagement_rate = (total_engagement / self.views) * 100
        else:
            self.engagement_rate = 0
        self.save()


class InfluencerProfile(TimeStampedUUIDModel):
    """Model to track influencers"""

    name = models.CharField(_('Name'), max_length=200)
    bio = models.TextField(_('Bio'), blank=True)
    category = models.CharField(_('Category'), max_length=100, blank=True,
                               help_text='e.g., Tech, Fashion, Food')

    # Social profiles
    twitter_username = models.CharField(_('Twitter Username'), max_length=100, blank=True)
    instagram_username = models.CharField(_('Instagram Username'), max_length=100, blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    youtube_channel = models.CharField(_('YouTube Channel'), max_length=200, blank=True)

    # Metrics
    total_followers = models.PositiveIntegerField(_('Total Followers'), default=0)
    average_engagement_rate = models.FloatField(_('Average Engagement Rate'), default=0.0)
    reach_potential = models.PositiveIntegerField(_('Reach Potential'), default=0)

    # Relationship
    relationship_status = models.CharField(_('Relationship Status'), max_length=20,
                                          choices=[
                                              ('prospect', 'Prospect'),
                                              ('contacted', 'Contacted'),
                                              ('collaborating', 'Collaborating'),
                                              ('inactive', 'Inactive'),
                                          ], default='prospect')
    contact_email = models.EmailField(_('Contact Email'), blank=True)

    # Campaign tracking
    campaigns_participated = models.ManyToManyField('social_media.Campaign',
                                                   related_name='influencers',
                                                   blank=True,
                                                   verbose_name=_('Campaigns'))

    # Team
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  related_name='tracked_influencers',
                                  verbose_name=_('Created By'))
    managed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='managed_influencers',
                                  verbose_name=_('Managed By'))

    class Meta:
        verbose_name = _('Influencer Profile')
        verbose_name_plural = _('Influencer Profiles')
        db_table = 'influencer_profiles'
        ordering = ['-total_followers']

    def __str__(self):
        return self.name


class InfluencerInteraction(TimeStampedUUIDModel):
    """Model to track interactions with influencers"""

    INTERACTION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('call', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('dm', 'Direct Message'),
        ('comment', 'Comment/Reply'),
    ]

    influencer = models.ForeignKey(InfluencerProfile, on_delete=models.CASCADE,
                                  related_name='interactions',
                                  verbose_name=_('Influencer'))
    interaction_type = models.CharField(_('Interaction Type'), max_length=20,
                                       choices=INTERACTION_TYPE_CHOICES)

    # Content
    subject = models.CharField(_('Subject'), max_length=200)
    notes = models.TextField(_('Notes'))

    # Metadata
    interaction_date = models.DateTimeField(_('Interaction Date'))
    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                           verbose_name=_('User'))

    # Follow-up
    requires_follow_up = models.BooleanField(_('Requires Follow-up'), default=False)
    follow_up_date = models.DateField(_('Follow-up Date'), null=True, blank=True)
    follow_up_completed = models.BooleanField(_('Follow-up Completed'), default=False)

    class Meta:
        verbose_name = _('Influencer Interaction')
        verbose_name_plural = _('Influencer Interactions')
        db_table = 'influencer_interactions'
        ordering = ['-interaction_date']

    def __str__(self):
        return f'{self.influencer.name} - {self.interaction_type} - {self.interaction_date.date()}'
