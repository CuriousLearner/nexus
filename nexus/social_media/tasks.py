# -*- coding: utf-8 -*-
# nexus Stuff
from nexus.celery import app
from nexus.social_media import services


@app.task(name='publish_on_social_media_task')
def publish_on_social_media_task():
    services.publish_on_social_media()


@app.task(name='publish_on_facebook_task',
          autoretry_for=(Exception, ),
          retry_kwargs={'max_retries': 3, 'countdown': 2 * 60})
def publish_on_facebook_task(post_id):
    services.publish_on_facebook(post_id)


@app.task(name='publish_on_linkedin_task',
          autoretry_for=(Exception, ),
          retry_kwargs={'max_retries': 3, 'countdown': 2 * 60})
def publish_on_linkedin_task(post_id):
    response = services.publish_on_linkedin(post_id)
    services.appropriate_response_action(response)
