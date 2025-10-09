# Standard Library
import io
from datetime import datetime, timedelta

# Third Party Stuff
from django.utils import timezone


def generate_performance_report_data(date_from, date_to, platforms=None):
    """
    Generate performance report data

    :param date_from: Start date
    :param date_to: End date
    :param platforms: List of platforms to include
    :returns: Dict with report data
    """
    from django.db.models import Avg, Count, Sum
    from nexus.social_media.analytics_models import PostAnalytics
    from nexus.social_media.models import Post

    # Get posts in date range
    posts = Post.objects.filter(
        posted_time__gte=date_from,
        posted_time__lte=date_to,
        is_posted=True
    )

    if platforms:
        from django.db.models import Q
        platform_filter = Q()
        for platform in platforms:
            platform_filter |= Q(posted_at=platform) | Q(platforms__contains=[platform])
        posts = posts.filter(platform_filter)

    # Overall metrics
    total_posts = posts.count()

    # Analytics aggregation
    analytics_data = PostAnalytics.objects.filter(
        post__in=posts
    ).aggregate(
        total_likes=Sum('likes'),
        total_shares=Sum('shares'),
        total_comments=Sum('comments'),
        total_views=Sum('views'),
        total_clicks=Sum('clicks'),
        total_reach=Sum('reach'),
        avg_engagement_rate=Avg('engagement_rate')
    )

    # Top performing posts
    top_posts = PostAnalytics.objects.filter(
        post__in=posts
    ).order_by('-engagement_rate')[:10].select_related('post')

    # Platform breakdown
    platform_stats = {}
    for platform_code, platform_name in [('fb', 'Facebook'), ('twitter', 'Twitter'),
                                         ('linkedin', 'LinkedIn'), ('instagram', 'Instagram'),
                                         ('threads', 'Threads')]:
        platform_posts = posts.filter(
            Q(posted_at=platform_code) | Q(platforms__contains=[platform_code])
        )
        platform_analytics = PostAnalytics.objects.filter(post__in=platform_posts).aggregate(
            count=Count('id'),
            total_engagement=Sum('likes') + Sum('shares') + Sum('comments'),
            avg_reach=Avg('reach')
        )
        if platform_analytics['count']:
            platform_stats[platform_name] = platform_analytics

    # Growth metrics (compare with previous period)
    period_length = (date_to - date_from).days
    previous_period_start = date_from - timedelta(days=period_length)
    previous_period_end = date_from

    previous_posts = Post.objects.filter(
        posted_time__gte=previous_period_start,
        posted_time__lte=previous_period_end,
        is_posted=True
    )

    if platforms:
        previous_posts = previous_posts.filter(platform_filter)

    previous_analytics = PostAnalytics.objects.filter(
        post__in=previous_posts
    ).aggregate(
        total_engagement=Sum('likes') + Sum('shares') + Sum('comments'),
        total_reach=Sum('reach')
    )

    # Calculate growth
    current_engagement = (analytics_data['total_likes'] or 0) + \
                        (analytics_data['total_shares'] or 0) + \
                        (analytics_data['total_comments'] or 0)
    previous_engagement = previous_analytics['total_engagement'] or 0

    engagement_growth = 0
    if previous_engagement > 0:
        engagement_growth = ((current_engagement - previous_engagement) / previous_engagement) * 100

    return {
        'period': {
            'from': date_from.isoformat(),
            'to': date_to.isoformat(),
        },
        'summary': {
            'total_posts': total_posts,
            'total_likes': analytics_data['total_likes'] or 0,
            'total_shares': analytics_data['total_shares'] or 0,
            'total_comments': analytics_data['total_comments'] or 0,
            'total_views': analytics_data['total_views'] or 0,
            'total_clicks': analytics_data['total_clicks'] or 0,
            'total_reach': analytics_data['total_reach'] or 0,
            'avg_engagement_rate': round(analytics_data['avg_engagement_rate'] or 0, 2),
        },
        'growth': {
            'engagement_growth': round(engagement_growth, 2),
            'previous_period_engagement': previous_engagement,
            'current_period_engagement': current_engagement,
        },
        'top_posts': [
            {
                'text': post.post.text[:100],
                'platform': post.post.posted_at or ','.join(post.post.platforms or []),
                'engagement_rate': round(post.engagement_rate, 2),
                'reach': post.reach,
                'likes': post.likes,
                'shares': post.shares,
                'comments': post.comments,
            }
            for post in top_posts
        ],
        'platform_breakdown': platform_stats,
    }


def generate_pdf_report(report_data, title='Social Media Performance Report'):
    """
    Generate PDF report from data

    Note: This is a simplified version. In production, you would use
    libraries like ReportLab, WeasyPrint, or xhtml2pdf

    :param report_data: Dict with report data
    :param title: Report title
    :returns: PDF file content
    """
    # Simplified HTML template
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #333; }}
            .metric-card {{ display: inline-block; margin: 10px; padding: 15px;
                           background: #f5f5f5; border-radius: 5px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
            .metric-label {{ color: #666; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p><strong>Period:</strong> {report_data['period']['from']} to {report_data['period']['to']}</p>

        <h2>Summary Metrics</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Posts</div>
                <div class="metric-value">{report_data['summary']['total_posts']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Reach</div>
                <div class="metric-value">{report_data['summary']['total_reach']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Likes</div>
                <div class="metric-value">{report_data['summary']['total_likes']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Engagement Rate</div>
                <div class="metric-value">{report_data['summary']['avg_engagement_rate']}%</div>
            </div>
        </div>

        <h2>Growth</h2>
        <p><strong>Engagement Growth:</strong> {report_data['growth']['engagement_growth']:.2f}%</p>

        <h2>Top Performing Posts</h2>
        <table>
            <tr>
                <th>Post</th>
                <th>Platform</th>
                <th>Engagement Rate</th>
                <th>Reach</th>
            </tr>
    """

    for post in report_data['top_posts'][:5]:
        html_content += f"""
            <tr>
                <td>{post['text']}</td>
                <td>{post['platform']}</td>
                <td>{post['engagement_rate']}%</td>
                <td>{post['reach']:,}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    # In production, convert HTML to PDF using a library like WeasyPrint:
    # from weasyprint import HTML
    # pdf = HTML(string=html_content).write_pdf()

    # For now, return the HTML content
    return html_content.encode('utf-8')


def generate_csv_report(report_data):
    """
    Generate CSV report from data

    :param report_data: Dict with report data
    :returns: CSV file content
    """
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    # Summary section
    writer.writerow(['Social Media Performance Report'])
    writer.writerow(['Period', f"{report_data['period']['from']} to {report_data['period']['to']}"])
    writer.writerow([])

    writer.writerow(['Summary Metrics'])
    writer.writerow(['Metric', 'Value'])
    for key, value in report_data['summary'].items():
        writer.writerow([key.replace('_', ' ').title(), value])

    writer.writerow([])
    writer.writerow(['Growth Metrics'])
    writer.writerow(['Metric', 'Value'])
    for key, value in report_data['growth'].items():
        writer.writerow([key.replace('_', ' ').title(), value])

    writer.writerow([])
    writer.writerow(['Top Performing Posts'])
    writer.writerow(['Post', 'Platform', 'Engagement Rate', 'Reach', 'Likes', 'Shares', 'Comments'])

    for post in report_data['top_posts']:
        writer.writerow([
            post['text'],
            post['platform'],
            post['engagement_rate'],
            post['reach'],
            post['likes'],
            post['shares'],
            post['comments']
        ])

    return output.getvalue().encode('utf-8')


def generate_dashboard_data(dashboard_id, date_from=None, date_to=None):
    """
    Generate data for dashboard widgets

    :param dashboard_id: Dashboard ID
    :param date_from: Start date
    :param date_to: End date
    :returns: Dict with widget data
    """
    from nexus.social_media.dashboard_models import Dashboard, DashboardWidget

    try:
        dashboard = Dashboard.objects.get(id=dashboard_id)
    except Dashboard.DoesNotExist:
        return {'error': 'Dashboard not found'}

    # Default date range
    if not date_to:
        date_to = timezone.now()
    if not date_from:
        date_from = date_to - timedelta(days=30)

    widget_data = {}

    for widget in dashboard.widgets.all():
        # Generate data based on widget type and metric
        data = None

        if widget.metric == 'total_posts':
            from nexus.social_media.models import Post
            count = Post.objects.filter(
                posted_time__gte=date_from,
                posted_time__lte=date_to
            ).count()
            data = {'value': count}

        elif widget.metric == 'engagement_rate':
            from nexus.social_media.analytics_models import PostAnalytics
            from django.db.models import Avg
            avg_rate = PostAnalytics.objects.filter(
                post__posted_time__gte=date_from,
                post__posted_time__lte=date_to
            ).aggregate(avg=Avg('engagement_rate'))
            data = {'value': round(avg_rate['avg'] or 0, 2)}

        elif widget.metric == 'total_reach':
            from nexus.social_media.analytics_models import PostAnalytics
            from django.db.models import Sum
            total = PostAnalytics.objects.filter(
                post__posted_time__gte=date_from,
                post__posted_time__lte=date_to
            ).aggregate(total=Sum('reach'))
            data = {'value': total['total'] or 0}

        widget_data[str(widget.id)] = {
            'widget_type': widget.widget_type,
            'title': widget.title,
            'data': data
        }

    # Update dashboard view count
    dashboard.view_count += 1
    dashboard.last_viewed_at = timezone.now()
    dashboard.save()

    return {
        'dashboard_id': str(dashboard.id),
        'dashboard_name': dashboard.name,
        'date_range': {
            'from': date_from.isoformat(),
            'to': date_to.isoformat()
        },
        'widgets': widget_data
    }
