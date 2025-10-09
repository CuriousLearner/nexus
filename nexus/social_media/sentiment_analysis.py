# Standard Library
import re
from collections import Counter
from datetime import timedelta

# Third Party Stuff
from django.db import models
from django.utils import timezone


def analyze_text_sentiment(text):
    """
    Analyze sentiment of text using keyword-based approach

    :param text: Text to analyze
    :returns: Dict with sentiment and score
    """
    if not text:
        return {'sentiment': 'neutral', 'score': 0.0}

    # Extended keyword lists
    positive_keywords = [
        'love', 'excellent', 'great', 'amazing', 'awesome', 'fantastic', 'wonderful',
        'good', 'nice', 'perfect', 'best', 'beautiful', 'incredible', 'outstanding',
        'brilliant', 'superb', 'pleased', 'happy', 'excited', 'thank', 'thanks',
        'appreciate', 'helpful', 'impressed', 'recommend', 'delighted'
    ]

    negative_keywords = [
        'hate', 'terrible', 'awful', 'bad', 'worst', 'horrible', 'disappointing',
        'disappointed', 'poor', 'useless', 'waste', 'annoying', 'frustrated',
        'angry', 'sad', 'upset', 'problem', 'issue', 'broken', 'fail', 'failed',
        'sucks', 'disgusting', 'pathetic', 'ridiculous', 'unacceptable'
    ]

    # Negation words that flip sentiment
    negation_words = ['not', 'no', 'never', 'neither', 'nobody', 'none', 'nothing', "n't"]

    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)

    positive_score = 0
    negative_score = 0

    for i, word in enumerate(words):
        # Check for negation before word
        is_negated = False
        if i > 0 and words[i-1] in negation_words:
            is_negated = True

        if word in positive_keywords:
            if is_negated:
                negative_score += 1
            else:
                positive_score += 1
        elif word in negative_keywords:
            if is_negated:
                positive_score += 1
            else:
                negative_score += 1

    # Calculate final score (-1 to 1)
    total = positive_score + negative_score
    if total == 0:
        return {'sentiment': 'neutral', 'score': 0.0}

    score = (positive_score - negative_score) / total

    # Determine sentiment category
    if score > 0.2:
        sentiment = 'positive'
    elif score < -0.2:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    return {'sentiment': sentiment, 'score': round(score, 2)}


def get_sentiment_trends(days=30):
    """
    Get sentiment trends over time

    :param days: Number of days to analyze
    :returns: Dict with daily sentiment data
    """
    from nexus.social_media.listening_models import SocialMention

    cutoff_date = timezone.now() - timedelta(days=days)
    mentions = SocialMention.objects.filter(
        created_at__gte=cutoff_date
    ).values('created_at__date', 'sentiment').annotate(
        count=models.Count('id')
    )

    # Organize by date and sentiment
    trends = {}
    for mention in mentions:
        date_str = mention['created_at__date'].isoformat()
        if date_str not in trends:
            trends[date_str] = {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'total': 0
            }

        sentiment = mention['sentiment']
        count = mention['count']
        trends[date_str][sentiment] = count
        trends[date_str]['total'] += count

    return trends


def get_sentiment_by_platform():
    """Get sentiment breakdown by platform"""
    from nexus.social_media.listening_models import SocialMention

    # Get mentions from last 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    mentions = SocialMention.objects.filter(
        created_at__gte=cutoff_date
    ).values('platform', 'sentiment').annotate(
        count=models.Count('id')
    )

    # Organize by platform
    platform_sentiment = {}
    for mention in mentions:
        platform = mention['platform']
        if platform not in platform_sentiment:
            platform_sentiment[platform] = {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'total': 0
            }

        sentiment = mention['sentiment']
        count = mention['count']
        platform_sentiment[platform][sentiment] = count
        platform_sentiment[platform]['total'] += count

    # Calculate percentages
    for platform, data in platform_sentiment.items():
        total = data['total']
        if total > 0:
            data['positive_pct'] = round((data['positive'] / total) * 100, 2)
            data['neutral_pct'] = round((data['neutral'] / total) * 100, 2)
            data['negative_pct'] = round((data['negative'] / total) * 100, 2)

    return platform_sentiment


def identify_sentiment_drivers(sentiment_type='negative', limit=20):
    """
    Identify most common phrases in positive or negative mentions

    :param sentiment_type: 'positive', 'negative', or 'neutral'
    :param limit: Number of top phrases to return
    :returns: List of common phrases/words
    """
    from nexus.social_media.listening_models import SocialMention

    # Get mentions with specified sentiment
    mentions = SocialMention.objects.filter(
        sentiment=sentiment_type
    ).values_list('text', flat=True)[:1000]  # Limit for performance

    # Extract words (filter stop words)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }

    all_words = []
    for text in mentions:
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        all_words.extend(filtered_words)

    # Get most common words
    word_freq = Counter(all_words)
    return word_freq.most_common(limit)


def get_sentiment_alerts():
    """
    Get sentiment-based alerts for recent negative mentions

    :returns: List of alerts
    """
    from nexus.social_media.listening_models import SocialMention

    alerts = []

    # Check for spikes in negative mentions
    last_hour = timezone.now() - timedelta(hours=1)
    recent_negative = SocialMention.objects.filter(
        sentiment='negative',
        created_at__gte=last_hour
    ).count()

    if recent_negative > 10:
        alerts.append({
            'type': 'negative_spike',
            'severity': 'high',
            'message': f'{recent_negative} negative mentions in the last hour',
            'timestamp': timezone.now()
        })

    # Check for unresponded negative mentions
    unresponded = SocialMention.objects.filter(
        sentiment='negative',
        is_responded=False,
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()

    if unresponded > 5:
        alerts.append({
            'type': 'unresponded_negative',
            'severity': 'medium',
            'message': f'{unresponded} negative mentions need response',
            'timestamp': timezone.now()
        })

    # Check for high-reach negative mentions
    high_reach_negative = SocialMention.objects.filter(
        sentiment='negative',
        author_followers__gt=10000,
        is_responded=False,
        created_at__gte=timezone.now() - timedelta(days=1)
    )

    if high_reach_negative.exists():
        alerts.append({
            'type': 'influencer_negative',
            'severity': 'high',
            'message': f'High-reach accounts ({high_reach_negative.count()}) posted negative mentions',
            'timestamp': timezone.now()
        })

    return alerts


def bulk_analyze_sentiment_for_mentions():
    """Analyze sentiment for mentions that don't have sentiment yet"""
    from nexus.social_media.listening_models import SocialMention

    unanalyzed = SocialMention.objects.filter(
        sentiment='unknown'
    )[:100]  # Process in batches

    for mention in unanalyzed:
        result = analyze_text_sentiment(mention.text)
        mention.sentiment = result['sentiment']
        mention.sentiment_score = result['score']
        mention.save()

    return len(unanalyzed)
