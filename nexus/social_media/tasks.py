# Third Party Stuff
from celery.decorators import task

# nexus Stuff
from nexus.social_media import services


@task()
def task_to_post_to_twitter(post_id):
    """Celery task to post on twitter.

    :param post_id: UUID of the post instance to be posted

    """
    services.post_to_twitter(post_id)
