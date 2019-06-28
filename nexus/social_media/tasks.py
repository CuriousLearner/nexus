# nexus Stuff
from nexus.celery import app
from nexus.social_media import services


@app.task(name='publish_posts_to_social_media_task')
def publish_posts_to_social_media_task():
    services.publish_posts_to_social_media()


@app.task(name='publish_posts_to_facebook_task')
def publish_posts_to_facebook_task(post_id):
    services.publish_posts_to_facebook(post_id)


@app.task(name='publish_posts_to_twitter_task')
def publish_posts_to_twitter_task(post_id):
    services.publish_posts_to_twitter(post_id)
