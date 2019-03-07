# nexus Stuff
from nexus.celery import app
from nexus.social_media.services import publish_posts_service


@app.task(name='publish_posts_task')
def publish_posts_task():
    """Celery task to call service to publish posts on social media."""
    publish_posts_service()
