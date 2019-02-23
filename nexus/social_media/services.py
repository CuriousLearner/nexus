# Third Party Stuff
import tweepy
from django.utils import timezone

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media.models import Post
from settings.development import TWITTER_OAUTH


def get_twitter_api_object(TWITTER_OAUTH):
    """Function to generate and return a twitter api object.

    :param TWITTER_OAUTH: a dictionary having essential twitter oauth token viz.
    consumer_key, consumer_secret, access_key, access_secret
    :returns: Twitter API object

    """
    auth = tweepy.OAuthHandler(TWITTER_OAUTH['consumer_key'], TWITTER_OAUTH['consumer_secret'])
    auth.set_access_token(TWITTER_OAUTH['access_key'], TWITTER_OAUTH['access_secret'])
    twitter_api = tweepy.API(auth)
    return twitter_api


def update_post_object(post):
    """Update post object after the post is posted"""
    post.posted_time = timezone.now()
    post.is_posted = True
    post.save()


def post_to_twitter(post_id):
    """Function to post on twitter.

    :params post_id: uuid of the post instance to be posted
    :returns: None
    :raises WrongArguments: exception for providing invalid arguments

    """
    post = Post.objects.get(pk=post_id)
    twitter_api = get_twitter_api_object(TWITTER_OAUTH)
    if twitter_api is False:
        raise exc.WrongArguments("Invalid Twitter Oauth Token(s).")

    if post.image:
        filename = post.image.file.name
        if post.text:
            twitter_api.update_with_media(filename=filename, status=post.text, file=post.image)
        else:
            twitter_api.update_with_media(filename=filename, file=post.image)
    elif post.text:
        twitter_api.update_status(status=post.text)

    update_post_object(post)
