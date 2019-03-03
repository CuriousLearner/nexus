# nexus Stuff
from nexus.celery import app
from nexus.social_media.services import publish_posts


@app.task(name='queue_posts')
def queue_posts():
    """Celery task to call services to publish posts on social media."""
    publish_posts()
