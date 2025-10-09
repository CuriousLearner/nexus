# Standard Library
import re
from collections import Counter
from datetime import timedelta

# Third Party Stuff
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class Hashtag(TimeStampedUUIDModel):
    """Model to track hashtags used in posts"""

    tag = models.CharField(_('Tag'), max_length=100, unique=True, db_index=True,
                          help_text='Hashtag without the # symbol')
    tag_lower = models.CharField(_('Tag (lowercase)'), max_length=100, db_index=True)

    # Usage stats
    total_uses = models.PositiveIntegerField(_('Total Uses'), default=0)
    total_posts = models.PositiveIntegerField(_('Total Posts'), default=0)
    first_used_at = models.DateTimeField(_('First Used At'), auto_now_add=True)
    last_used_at = models.DateTimeField(_('Last Used At'), auto_now=True)

    # Performance metrics (aggregated from PostHashtag)
    total_impressions = models.BigIntegerField(_('Total Impressions'), default=0)
    total_engagements = models.BigIntegerField(_('Total Engagements'), default=0)
    total_clicks = models.BigIntegerField(_('Total Clicks'), default=0)

    # Categorization
    category = models.CharField(_('Category'), max_length=50, blank=True,
                               help_text='e.g., Technology, Marketing, Events')
    is_trending = models.BooleanField(_('Is Trending'), default=False)
    is_banned = models.BooleanField(_('Is Banned'), default=False,
                                   help_text='Flag inappropriate hashtags')

    class Meta:
        verbose_name = _('Hashtag')
        verbose_name_plural = _('Hashtags')
        db_table = 'hashtags'
        ordering = ['-total_uses', '-last_used_at']
        indexes = [
            models.Index(fields=['-total_uses']),
            models.Index(fields=['-last_used_at']),
        ]

    def __str__(self):
        return f'#{self.tag}'

    def save(self, *args, **kwargs):
        # Ensure lowercase version is saved
        self.tag_lower = self.tag.lower()
        super().save(*args, **kwargs)

    def get_engagement_rate(self):
        """Calculate average engagement rate"""
        if self.total_impressions == 0:
            return 0
        return (self.total_engagements / self.total_impressions) * 100

    def get_trending_score(self):
        """Calculate trending score based on recent usage"""
        # Get usage in last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_uses = PostHashtag.objects.filter(
            hashtag=self,
            created_at__gte=seven_days_ago
        ).count()

        # Simple trending score: recent_uses * engagement_rate
        return recent_uses * self.get_engagement_rate()


class PostHashtag(TimeStampedUUIDModel):
    """Many-to-many relationship between Posts and Hashtags with metrics"""

    post = models.ForeignKey('social_media.Post', on_delete=models.CASCADE,
                            related_name='post_hashtags', verbose_name=_('Post'))
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE,
                               related_name='post_hashtags', verbose_name=_('Hashtag'))

    # Platform-specific metrics
    platform = models.CharField(_('Platform'), max_length=20, blank=True,
                               choices=[
                                   ('fb', 'Facebook'),
                                   ('twitter', 'Twitter'),
                                   ('linkedin', 'Linkedin'),
                                   ('instagram', 'Instagram'),
                                   ('threads', 'Threads'),
                               ])

    # Performance metrics
    impressions = models.BigIntegerField(_('Impressions'), default=0)
    engagements = models.BigIntegerField(_('Engagements'), default=0,
                                        help_text='Likes, shares, comments')
    clicks = models.BigIntegerField(_('Clicks'), default=0)
    reach = models.BigIntegerField(_('Reach'), default=0)

    class Meta:
        verbose_name = _('Post Hashtag')
        verbose_name_plural = _('Post Hashtags')
        db_table = 'post_hashtags'
        unique_together = [['post', 'hashtag', 'platform']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'hashtag']),
            models.Index(fields=['-impressions']),
        ]

    def __str__(self):
        return f'{self.post.text[:30]} - #{self.hashtag.tag}'


class HashtagPerformanceSnapshot(TimeStampedUUIDModel):
    """Daily snapshot of hashtag performance for trend analysis"""

    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE,
                               related_name='performance_snapshots',
                               verbose_name=_('Hashtag'))
    snapshot_date = models.DateField(_('Snapshot Date'))

    # Daily metrics
    daily_uses = models.PositiveIntegerField(_('Daily Uses'), default=0)
    daily_posts = models.PositiveIntegerField(_('Daily Posts'), default=0)
    daily_impressions = models.BigIntegerField(_('Daily Impressions'), default=0)
    daily_engagements = models.BigIntegerField(_('Daily Engagements'), default=0)
    daily_clicks = models.BigIntegerField(_('Daily Clicks'), default=0)

    # Ranking
    trending_rank = models.PositiveIntegerField(_('Trending Rank'), null=True, blank=True)

    class Meta:
        verbose_name = _('Hashtag Performance Snapshot')
        verbose_name_plural = _('Hashtag Performance Snapshots')
        db_table = 'hashtag_performance_snapshots'
        unique_together = [['hashtag', 'snapshot_date']]
        ordering = ['-snapshot_date', 'trending_rank']
        indexes = [
            models.Index(fields=['-snapshot_date']),
            models.Index(fields=['trending_rank']),
        ]

    def __str__(self):
        return f'#{self.hashtag.tag} - {self.snapshot_date}'


def extract_hashtags(text):
    """
    Extract hashtags from text

    :param text: Text to extract hashtags from
    :returns: List of hashtag strings (without #)
    """
    if not text:
        return []

    # Regex pattern for hashtags
    # Matches # followed by alphanumeric characters and underscores
    pattern = r'#(\w+)'
    hashtags = re.findall(pattern, text)

    return list(set(hashtags))  # Remove duplicates


def process_post_hashtags(post):
    """
    Process and create hashtag relationships for a post

    :param post: Post instance
    :returns: List of Hashtag instances
    """
    from nexus.social_media.models import Post

    if not isinstance(post, Post):
        raise ValueError("post must be a Post instance")

    hashtags_in_text = extract_hashtags(post.text)
    created_hashtags = []

    for tag in hashtags_in_text:
        # Get or create hashtag
        hashtag, created = Hashtag.objects.get_or_create(
            tag_lower=tag.lower(),
            defaults={'tag': tag}
        )

        # Update usage stats
        hashtag.total_uses += 1
        hashtag.last_used_at = timezone.now()
        hashtag.save()

        # Create PostHashtag relationship
        if post.platforms:
            # Create entry for each platform
            for platform in post.platforms:
                PostHashtag.objects.get_or_create(
                    post=post,
                    hashtag=hashtag,
                    platform=platform
                )
        else:
            # Create single entry
            PostHashtag.objects.get_or_create(
                post=post,
                hashtag=hashtag,
                platform=post.posted_at or ''
            )

        created_hashtags.append(hashtag)

    # Update total posts count
    for hashtag in created_hashtags:
        hashtag.total_posts = PostHashtag.objects.filter(
            hashtag=hashtag
        ).values('post').distinct().count()
        hashtag.save()

    return created_hashtags


def get_trending_hashtags(limit=10, days=7):
    """
    Get trending hashtags based on recent activity

    :param limit: Number of hashtags to return
    :param days: Number of days to look back
    :returns: QuerySet of trending hashtags
    """
    cutoff_date = timezone.now() - timedelta(days=days)

    # Get hashtags with recent activity
    trending = Hashtag.objects.filter(
        last_used_at__gte=cutoff_date,
        is_banned=False
    ).annotate(
        recent_posts=models.Count(
            'post_hashtags',
            filter=models.Q(post_hashtags__created_at__gte=cutoff_date)
        )
    ).filter(
        recent_posts__gt=0
    ).order_by('-recent_posts', '-total_engagements')[:limit]

    return trending


def get_hashtag_suggestions(post_text, limit=5):
    """
    Suggest hashtags based on post content and historical performance

    :param post_text: Post text to analyze
    :param limit: Number of suggestions to return
    :returns: List of suggested hashtag strings
    """
    if not post_text:
        return []

    # Extract keywords from post text
    words = re.findall(r'\b[a-zA-Z]{3,}\b', post_text.lower())
    word_freq = Counter(words)

    suggestions = []

    # Find hashtags that match keywords
    for word, _ in word_freq.most_common():
        matching_hashtags = Hashtag.objects.filter(
            tag_lower__icontains=word,
            is_banned=False
        ).order_by('-total_uses', '-total_engagements')[:2]

        for hashtag in matching_hashtags:
            if len(suggestions) >= limit:
                break
            if hashtag.tag not in suggestions:
                suggestions.append(hashtag.tag)

        if len(suggestions) >= limit:
            break

    # Fill remaining with top performing hashtags
    if len(suggestions) < limit:
        top_hashtags = Hashtag.objects.filter(
            is_banned=False
        ).order_by('-total_engagements')[:limit - len(suggestions)]

        for hashtag in top_hashtags:
            if hashtag.tag not in suggestions:
                suggestions.append(hashtag.tag)

    return suggestions


def create_daily_snapshots():
    """
    Create daily performance snapshots for all active hashtags
    Called by scheduled task
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Get all hashtags used yesterday
    hashtags = Hashtag.objects.filter(
        last_used_at__date=yesterday
    )

    for hashtag in hashtags:
        # Calculate daily metrics
        daily_post_hashtags = PostHashtag.objects.filter(
            hashtag=hashtag,
            created_at__date=yesterday
        )

        daily_uses = daily_post_hashtags.count()
        daily_posts = daily_post_hashtags.values('post').distinct().count()

        # Aggregate metrics
        metrics = daily_post_hashtags.aggregate(
            impressions=models.Sum('impressions'),
            engagements=models.Sum('engagements'),
            clicks=models.Sum('clicks')
        )

        # Create snapshot
        HashtagPerformanceSnapshot.objects.update_or_create(
            hashtag=hashtag,
            snapshot_date=yesterday,
            defaults={
                'daily_uses': daily_uses,
                'daily_posts': daily_posts,
                'daily_impressions': metrics['impressions'] or 0,
                'daily_engagements': metrics['engagements'] or 0,
                'daily_clicks': metrics['clicks'] or 0,
            }
        )

    # Update trending ranks
    trending = get_trending_hashtags(limit=50)
    for rank, hashtag in enumerate(trending, start=1):
        snapshot = HashtagPerformanceSnapshot.objects.filter(
            hashtag=hashtag,
            snapshot_date=yesterday
        ).first()

        if snapshot:
            snapshot.trending_rank = rank
            snapshot.save()

        # Update is_trending flag
        hashtag.is_trending = rank <= 10
        hashtag.save()
