# nexus Stuff
from nexus.celery import app
from nexus.social_media.services import publish_post_service


@app.task(name='publish_posts')
def publish_posts_to_social_media():
    """Celery task to call service to publish post on social media"""
    publish_post_service()
