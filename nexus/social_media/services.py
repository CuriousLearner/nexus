# Standard Library
from datetime import datetime

# Third Party Stuff
import facebook
import tweepy
from django.conf import settings
from django.utils import timezone

# nexus Stuff
from nexus.base import exceptions
from nexus.social_media import tasks
from nexus.social_media.models import Post


def get_twitter_api_object(TWITTER_OAUTH):
    """Function to generate a twitter API object.

    :param TWITTER_OAUTH: A dictionary having essential twitter oauth tokens viz.
    consumer_key, consumer_secret, access_key, access_secret.

    :returns: twitter API object.

    :raises WrongArguments: Exception, when invalid twitter oauth token(s) are provided.

    """
    try:
        auth = tweepy.OAuthHandler(TWITTER_OAUTH['consumer_key'], TWITTER_OAUTH['consumer_secret'])
        auth.set_access_token(TWITTER_OAUTH['access_key'], TWITTER_OAUTH['access_secret'])
        twitter_api = tweepy.API(auth)
        return twitter_api
    except tweepy.error.TweepError as exc:
        raise exceptions.WrongArguments("TweepError: Invalid Twitter OAuth Token(s). Reason: " + str(exc))


def publish_on_twitter(post_id):
    """Function to post on twitter.

    :param post_id: UUID of the post instance to be posted.

    :raises BadRequest: Exception, when unable to post to twitter using tweepy.

    """
    post = Post.objects.get(pk=post_id)
    twitter_api = get_twitter_api_object(settings.TWITTER_OAUTH)

    try:
        if post.image:
            filename = post.image.file.name
            twitter_api.update_with_media(filename=filename, status=post.text, file=post.image)
        elif post.text:
            twitter_api.update_status(status=post.text)

    except tweepy.error.TweepError as exc:
        raise exceptions.BadRequest("TweepError: Unable to publish post on twitter. Reason: " + str(exc))


def get_fb_page_graph():
    graph = facebook.GraphAPI(settings.FB_USER_ACCESS_TOKEN)
    pages = graph.get_object('me/accounts')['data']
    page_access_token = None
    page_list = list(filter(lambda page: page['id'] == settings.FB_PAGE_ID, pages))
    if not page_list:
        raise exceptions.WrongArguments("Facebook Page access token could not be found")
    page_access_token = page_list[0]['access_token']
    page_graph = facebook.GraphAPI(page_access_token)
    return page_graph


def publish_on_facebook(post_id):
    post = Post.objects.get(pk=post_id)
    page_graph = get_fb_page_graph()
    if post.image:
        if post.text:
            page_graph.put_photo(image=post.image.file.open('rb'), message=post.text)
        else:
            page_graph.put_photo(image=post.image.file.open('rb'))
    elif post.text:
        page_graph.put_object(
            parent_object=settings.FB_PAGE_ID, connection_name='feed', message=post.text
        )


def publish_on_social_media():
    if settings.LIMIT_POSTS is True and int(settings.MAX_POSTS_AT_ONCE) > 0:
        posts = Post.objects.filter(
            is_approved=True, is_posted=False, scheduled_time__lte=datetime.now()
        )[:int(settings.MAX_POSTS_AT_ONCE)]
    else:
        posts = Post.objects.filter(
            is_approved=True, is_posted=False, scheduled_time__lte=datetime.now()
        )

    # Before bulk update, saving the IDs of posts along with there publishing platforms.
    post_platform = {}
    for post in posts:
        post_platform.update({post.id: post.posted_at})

    if settings.LIMIT_POSTS is True and int(settings.MAX_POSTS_AT_ONCE) > 0:
        Post.objects.filter(id__in=posts).update(is_posted=True, posted_time=timezone.now())
    else:
        posts.update(is_posted=True, posted_time=timezone.now())

    for post_id in post_platform:
        if post_platform[post_id] == 'fb':
            tasks.publish_on_facebook_task.delay(post_id)
        elif post_platform[post_id] == 'twitter':
            tasks.publish_on_twitter_task.delay(post_id)
