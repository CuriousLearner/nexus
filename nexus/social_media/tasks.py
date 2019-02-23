# Third Party Stuff
import celery
from celery.decorators import task

# nexus Stuff
from nexus.social_media import services


class BaseTask(celery.Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))


@task(base=BaseTask)
def task_to_post_to_twitter(post_id):
    """Celery task to post on twitter.

    :params post_id: uuid of the post instance to be posted

    """
    services.post_to_twitter(post_id)
