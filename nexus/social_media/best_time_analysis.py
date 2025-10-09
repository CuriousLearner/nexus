# Standard Library
from collections import defaultdict
from datetime import datetime, timedelta

# Third Party Stuff
from django.db import models
from django.utils import timezone


def analyze_best_posting_times(platform=None, days=90):
    """
    Analyze historical post performance to determine best times to post

    :param platform: Platform to analyze (None for all)
    :param days: Number of days of history to analyze
    :returns: Dict with best times and engagement data
    """
    from nexus.social_media.analytics_models import PostAnalytics
    from nexus.social_media.models import Post

    cutoff_date = timezone.now() - timedelta(days=days)

    # Get posts with analytics
    posts = Post.objects.filter(
        is_posted=True,
        posted_time__gte=cutoff_date
    ).select_related('analytics')

    if platform:
        posts = posts.filter(
            models.Q(posted_at=platform) | models.Q(platforms__contains=[platform])
        )

    # Organize by hour and day of week
    time_performance = defaultdict(lambda: {
        'total_posts': 0,
        'total_engagement': 0,
        'total_reach': 0,
        'avg_engagement_rate': 0
    })

    for post in posts:
        if not hasattr(post, 'analytics') or not post.posted_time:
            continue

        analytics = post.analytics
        posted_time = post.posted_time

        # Get day of week (0=Monday, 6=Sunday) and hour
        day_of_week = posted_time.weekday()
        hour = posted_time.hour

        key = f'{day_of_week}_{hour}'

        time_performance[key]['total_posts'] += 1
        time_performance[key]['total_engagement'] += (
            analytics.likes + analytics.shares + analytics.comments
        )
        time_performance[key]['total_reach'] += analytics.reach

        if analytics.reach > 0:
            engagement_rate = (
                (analytics.likes + analytics.shares + analytics.comments) / analytics.reach
            ) * 100
            time_performance[key]['avg_engagement_rate'] += engagement_rate

    # Calculate averages
    for key, data in time_performance.items():
        if data['total_posts'] > 0:
            data['avg_engagement'] = data['total_engagement'] / data['total_posts']
            data['avg_reach'] = data['total_reach'] / data['total_posts']
            data['avg_engagement_rate'] = data['avg_engagement_rate'] / data['total_posts']

    return dict(time_performance)


def get_best_posting_schedule(platform=None, posts_per_week=7):
    """
    Generate recommended posting schedule

    :param platform: Platform to optimize for
    :param posts_per_week: Number of posts per week
    :returns: List of recommended posting times
    """
    time_performance = analyze_best_posting_times(platform=platform)

    # Sort by engagement rate
    sorted_times = sorted(
        time_performance.items(),
        key=lambda x: x[1]['avg_engagement_rate'],
        reverse=True
    )

    # Get top performing times
    recommendations = []
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    for i, (key, data) in enumerate(sorted_times[:posts_per_week]):
        if data['total_posts'] < 3:  # Need minimum sample size
            continue

        day_of_week, hour = map(int, key.split('_'))

        recommendations.append({
            'rank': i + 1,
            'day_of_week': day_of_week,
            'day_name': day_names[day_of_week],
            'hour': hour,
            'time': f'{hour:02d}:00',
            'avg_engagement_rate': round(data['avg_engagement_rate'], 2),
            'avg_reach': int(data['avg_reach']),
            'sample_size': data['total_posts']
        })

    return recommendations


def get_platform_specific_insights():
    """Get best times to post for each platform"""
    platforms = ['fb', 'twitter', 'linkedin', 'instagram', 'threads']

    insights = {}
    for platform in platforms:
        schedule = get_best_posting_schedule(platform=platform, posts_per_week=5)
        if schedule:
            insights[platform] = {
                'best_times': schedule[:5],
                'total_analyzed': sum(s['sample_size'] for s in schedule)
            }

    return insights


def get_audience_activity_patterns(platform=None):
    """
    Analyze when audience is most active based on engagement patterns

    :param platform: Platform to analyze
    :returns: Dict with activity patterns
    """
    time_performance = analyze_best_posting_times(platform=platform, days=60)

    # Group by hour across all days
    hourly_activity = defaultdict(lambda: {
        'total_engagement': 0,
        'total_posts': 0,
        'avg_engagement': 0
    })

    for key, data in time_performance.items():
        _, hour = map(int, key.split('_'))
        hourly_activity[hour]['total_engagement'] += data['total_engagement']
        hourly_activity[hour]['total_posts'] += data['total_posts']

    # Calculate averages
    for hour, data in hourly_activity.items():
        if data['total_posts'] > 0:
            data['avg_engagement'] = data['total_engagement'] / data['total_posts']

    # Find peak hours
    sorted_hours = sorted(
        hourly_activity.items(),
        key=lambda x: x[1]['avg_engagement'],
        reverse=True
    )

    peak_hours = [
        {
            'hour': hour,
            'time': f'{hour:02d}:00 - {(hour+1):02d}:00',
            'avg_engagement': round(data['avg_engagement'], 2),
            'sample_size': data['total_posts']
        }
        for hour, data in sorted_hours[:6] if data['total_posts'] >= 3
    ]

    return {
        'peak_hours': peak_hours,
        'hourly_breakdown': dict(hourly_activity)
    }


def get_day_of_week_performance(platform=None):
    """Analyze performance by day of week"""
    time_performance = analyze_best_posting_times(platform=platform)

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_performance = defaultdict(lambda: {
        'total_engagement': 0,
        'total_reach': 0,
        'total_posts': 0,
        'avg_engagement': 0,
        'avg_reach': 0,
        'avg_engagement_rate': 0
    })

    # Aggregate by day
    for key, data in time_performance.items():
        day_of_week, _ = map(int, key.split('_'))
        daily_performance[day_of_week]['total_engagement'] += data['total_engagement']
        daily_performance[day_of_week]['total_reach'] += data['total_reach']
        daily_performance[day_of_week]['total_posts'] += data['total_posts']
        daily_performance[day_of_week]['avg_engagement_rate'] += (
            data['avg_engagement_rate'] * data['total_posts']
        )

    # Calculate averages
    results = []
    for day in range(7):
        data = daily_performance[day]
        if data['total_posts'] > 0:
            results.append({
                'day_of_week': day,
                'day_name': day_names[day],
                'avg_engagement': round(data['total_engagement'] / data['total_posts'], 2),
                'avg_reach': round(data['total_reach'] / data['total_posts'], 2),
                'avg_engagement_rate': round(data['avg_engagement_rate'] / data['total_posts'], 2),
                'total_posts': data['total_posts']
            })

    # Sort by engagement rate
    results.sort(key=lambda x: x['avg_engagement_rate'], reverse=True)

    return results


def predict_post_performance(scheduled_time, platform=None):
    """
    Predict expected performance for a post at given time

    :param scheduled_time: Datetime when post is scheduled
    :param platform: Platform to post on
    :returns: Dict with predicted metrics
    """
    time_performance = analyze_best_posting_times(platform=platform)

    day_of_week = scheduled_time.weekday()
    hour = scheduled_time.hour
    key = f'{day_of_week}_{hour}'

    if key in time_performance:
        data = time_performance[key]

        # Check if we have enough data
        if data['total_posts'] < 3:
            return {
                'confidence': 'low',
                'message': 'Not enough historical data for this time slot',
                'sample_size': data['total_posts']
            }

        return {
            'confidence': 'high' if data['total_posts'] >= 10 else 'medium',
            'predicted_engagement_rate': round(data['avg_engagement_rate'], 2),
            'predicted_reach': int(data['avg_reach']),
            'predicted_engagement': int(data['avg_engagement']),
            'sample_size': data['total_posts'],
            'recommendation': 'optimal' if data['avg_engagement_rate'] > 3 else 'suboptimal'
        }

    return {
        'confidence': 'none',
        'message': 'No historical data for this time slot',
        'sample_size': 0
    }


def get_optimal_frequency(platform=None):
    """
    Determine optimal posting frequency based on historical data

    :param platform: Platform to analyze
    :returns: Dict with frequency recommendations
    """
    from nexus.social_media.models import Post

    # Analyze last 60 days
    cutoff_date = timezone.now() - timedelta(days=60)

    posts = Post.objects.filter(
        is_posted=True,
        posted_time__gte=cutoff_date
    ).select_related('analytics')

    if platform:
        posts = posts.filter(
            models.Q(posted_at=platform) | models.Q(platforms__contains=[platform])
        )

    # Group posts by week and calculate average engagement
    weekly_data = defaultdict(lambda: {
        'posts': [],
        'avg_engagement_rate': 0
    })

    for post in posts:
        if not hasattr(post, 'analytics') or not post.posted_time:
            continue

        # Get week number
        week_key = post.posted_time.isocalendar()[1]
        analytics = post.analytics

        if analytics.reach > 0:
            engagement_rate = (
                (analytics.likes + analytics.shares + analytics.comments) / analytics.reach
            ) * 100
            weekly_data[week_key]['posts'].append(engagement_rate)

    # Calculate average engagement by post frequency
    frequency_performance = defaultdict(list)

    for week, data in weekly_data.items():
        post_count = len(data['posts'])
        if post_count > 0:
            avg_engagement = sum(data['posts']) / post_count
            frequency_performance[post_count].append(avg_engagement)

    # Find optimal frequency
    optimal_freq = None
    best_engagement = 0

    for freq, engagement_rates in frequency_performance.items():
        avg = sum(engagement_rates) / len(engagement_rates)
        if avg > best_engagement:
            best_engagement = avg
            optimal_freq = freq

    return {
        'optimal_posts_per_week': optimal_freq,
        'expected_engagement_rate': round(best_engagement, 2),
        'frequency_breakdown': {
            freq: {
                'avg_engagement_rate': round(sum(rates) / len(rates), 2),
                'weeks_analyzed': len(rates)
            }
            for freq, rates in frequency_performance.items()
        }
    }
