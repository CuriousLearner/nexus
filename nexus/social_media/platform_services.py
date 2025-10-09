# -*- coding: utf-8 -*-
# Third Party Stuff
import requests
from django.conf import settings
from django.utils import timezone

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media.models import Post
from nexus.social_media.schedule_models import PlatformSchedule


def publish_on_threads(post_id):
    """Function to post on Threads (Meta's Twitter competitor).

    :param post_id: UUID of the post instance to be posted.

    :raises BadRequest: Exception, when unable to post to Threads.

    """
    post = Post.objects.get(pk=post_id)

    # Threads API endpoint (using Instagram Graph API)
    url = f"https://graph.threads.net/{settings.THREADS_USER_ID}/threads"

    payload = {
        'media_type': 'TEXT',
        'text': post.text,
        'access_token': settings.THREADS_ACCESS_TOKEN
    }

    if post.image:
        payload['media_type'] = 'IMAGE'
        payload['image_url'] = post.image.url

    try:
        # Create thread container
        response = requests.post(url, data=payload)
        response.raise_for_status()
        container_id = response.json().get('id')

        # Publish the thread
        publish_url = f"https://graph.threads.net/{settings.THREADS_USER_ID}/threads_publish"
        publish_payload = {
            'creation_id': container_id,
            'access_token': settings.THREADS_ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        publish_response.raise_for_status()

    except Exception as exc_info:
        raise exc.BadRequest(str(exc_info))


def publish_platform_schedules():
    """Process platform-specific schedules and publish posts"""
    from nexus.social_media import tasks

    # Get all scheduled posts that are due and not yet posted
    schedules = PlatformSchedule.objects.filter(
        is_posted=False,
        scheduled_time__lte=timezone.now(),
        post__is_approved=True,
        post__is_draft=False
    ).select_related('post')

    for schedule in schedules:
        # Publish to specific platform
        if schedule.platform == 'fb':
            tasks.publish_on_facebook_task.delay(str(schedule.post.id))
        elif schedule.platform == 'twitter':
            tasks.publish_on_twitter_task.delay(str(schedule.post.id))
        elif schedule.platform == 'linkedin':
            tasks.publish_on_linkedin_task.delay(str(schedule.post.id))
        elif schedule.platform == 'instagram':
            tasks.publish_on_instagram_task.delay(str(schedule.post.id))
        elif schedule.platform == 'threads':
            tasks.publish_on_threads_task.delay(str(schedule.post.id))

        # Mark as posted
        schedule.is_posted = True
        schedule.posted_time = timezone.now()
        schedule.save()
