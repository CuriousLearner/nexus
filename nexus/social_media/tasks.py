# nexus Stuff
from nexus.celery import app
from nexus.social_media.services import service_to_publish_posts


@app.task(name='task_to_publish_posts')
def task_to_publish_posts():
    """Celery task to call service to publish posts on social media."""
    service_to_publish_posts()
