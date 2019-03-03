# Third Party Stuff
import tweepy
from django.utils import timezone

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media.models import Post
from settings.development import TWITTER_OAUTH


def update_post_object(post):
    """Update post instance after the post is published.

    :param post: Post model instance

    """
    post.posted_time = timezone.now()
    post.is_posted = True
    post.save()


def get_twitter_api_object(TWITTER_OAUTH):
    """Function to generate a twitter api object.

    :param TWITTER_OAUTH: A dictionary having essential twitter oauth token viz.
    consumer_key, consumer_secret, access_key, access_secret.

    :returns: twitter API object.

    :raises WrongArguments: Exception, when invalid twitter token are provided.

    """
    try:
        auth = tweepy.OAuthHandler(TWITTER_OAUTH['consumer_key'], TWITTER_OAUTH['consumer_secret'])
        auth.set_access_token(TWITTER_OAUTH['access_key'], TWITTER_OAUTH['access_secret'])
        twitter_api = tweepy.API(auth)
        return twitter_api
    except tweepy.error.TweepError:
        raise exc.WrongArguments("Invalid Twitter Oauth Token(s).")


def post_to_twitter(post_id):
    """Function to post on twitter.

    :param post_id: UUID of the post instance to be posted

    :raises BadRequest: Exception, when unable to post to twitter.

    """
    post = Post.objects.get(pk=post_id)
    twitter_api = get_twitter_api_object(TWITTER_OAUTH)

    try:
        if post.image:
            filename = post.image.file.name
            if post.text:
                twitter_api.update_with_media(filename=filename, status=post.text, file=post.image)
            else:
                twitter_api.update_with_media(filename=filename, file=post.image)
        elif post.text:
            twitter_api.update_status(status=post.text)
        update_post_object(post)

    except tweepy.error.TweepError:
        raise exc.BadRequest("TweepError: Tweeter post couldn't published!")


def publish_posts():
    """Function to publish social media posts."""
    posts = Post.objects.filter(
        is_approved=True, is_posted=False, scheduled_time__lte=timezone.now()
    )
    for post in posts:
        if post.posted_at == 'twitter':
            post_to_twitter(post.id)
        # if post.posted_at == 'fb':
        #     post_to_facebook(post.id)
