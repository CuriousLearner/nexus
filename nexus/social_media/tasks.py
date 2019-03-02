# Standard Library
from datetime import datetime

# Nexus Stuff
from nexus.social_media.models import Post
from nexus.social_media.services import post_to_facebook
from nexus.celery import app
from settings.common import MAX_POSTS_AT_ONCE
# from nexus.social_media.services import post_to_twitter


@app.task(name='queue_posts')
def queue_posts():
    posts = Post.objects.filter(
        is_approved=True, is_posted=False, scheduled_time__lte=datetime.now()
    )[:MAX_POSTS_AT_ONCE]
    for post in posts:
        if post.posted_at == 'fb':
            post_to_facebook.delay(post.id)
        # if post.posted_at == 'twitter':
        #     post_to_twitter.delay(post.id)
        post.is_posted = True
        post.save()
