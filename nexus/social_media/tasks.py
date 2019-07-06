# Standard Library
from datetime import datetime

# Third Party Stuff
from django.conf import settings

# nexus Stuff
from nexus.celery import app
from nexus.social_media.services import publish_post_service
from nexus.social_media.models import Post
from nexus.social_media.services import post_to_facebook


@app.task(name='publish_posts_task')
def publish_posts_to_social_media():
    """Celery task to call service to publish post on social media"""
    publish_post_service()


@app.task(name='publish_posts_to_social_media')
def publish_posts_to_social_media_new():
    if settings.LIMIT_POSTS is True and int(settings.MAX_POSTS_AT_ONCE) > 0:
        posts = Post.objects.filter(
            is_approved=True, is_posted=False, scheduled_time__lte=datetime.now()
        )[:int(settings.MAX_POSTS_AT_ONCE)]
    else:
        posts = Post.objects.filter(
            is_approved=True, is_posted=False, scheduled_time__lte=datetime.now()
        )

    for post in posts:
        if post.posted_at == 'fb':
            post_to_facebook(post.id)
        post.is_posted = True
        post.posted_time = datetime.now()
        post.save()
