# -*- coding: utf-8 -*-
# Standard Library
from unittest import mock

# Third Party Stuff
import pytest
import tweepy
from django.conf import settings
from tests import factories as f

# nexus Stuff
from nexus.base import exceptions
from nexus.social_media import services, tasks
from nexus.social_media.models import Post

pytestmark = pytest.mark.django_db


@mock.patch('nexus.social_media.services.tweepy.API')
@mock.patch('nexus.social_media.services.tweepy.OAuthHandler.set_access_token')
@mock.patch('nexus.social_media.services.tweepy.OAuthHandler')
def test_get_twitter_api_object(mock_oauthhandler, mock_set_access_token, mock_api):
    mock_oauthhandler.return_value = tweepy.OAuthHandler
    services.get_twitter_api_object(settings.TWITTER_OAUTH)

    mock_oauthhandler.assert_called_once_with(
        settings.TWITTER_OAUTH['consumer_key'], settings.TWITTER_OAUTH['consumer_secret']
    )
    mock_set_access_token.assert_called_once_with(
        settings.TWITTER_OAUTH['access_key'], settings.TWITTER_OAUTH['access_secret']
    )
    mock_api.assert_called_once_with(mock_oauthhandler)

    mock_api.side_effect = tweepy.error.TweepError('Error reason from twitter')

    with pytest.raises(exceptions.WrongArguments) as exc:
        services.get_twitter_api_object(settings.TWITTER_OAUTH)
    assert exc.value.args[0] == 'Error reason from twitter'


@mock.patch('nexus.social_media.services.tweepy.api.update_with_media')
@mock.patch('nexus.social_media.services.tweepy.api.update_status')
@mock.patch('nexus.social_media.services.get_twitter_api_object')
def test_publish_on_twitter_service(mock_get_twitter_api_object, mock_update_status, mock_update_with_media):
    mock_get_twitter_api_object.return_value = tweepy.api

    # Check post only with text
    post = f.create_post(image=None)
    services.publish_on_twitter(post.id)
    mock_get_twitter_api_object.assert_called_once_with(settings.TWITTER_OAUTH)
    mock_update_status.assert_called_once_with(status=post.text)

    # Check post with text and image
    post = f.create_post()
    post_instance = Post.objects.get(pk=post.id)
    image_file = post_instance.image.file.name

    mock_get_twitter_api_object.reset_mock()
    services.publish_on_twitter(post.id)
    mock_get_twitter_api_object.assert_called_once_with(settings.TWITTER_OAUTH)
    mock_update_with_media.assert_called_once_with(
        filename=image_file, status=post.text, file=post_instance.image
    )

    # Raising a TweepError
    mock_update_with_media.side_effect = tweepy.error.TweepError('Error reason from twitter')
    with pytest.raises(exceptions.BadRequest) as exc:
        services.publish_on_twitter(post.id)
    assert exc.value.args[0] == 'Error reason from twitter'


@mock.patch('nexus.social_media.services.tasks.publish_on_twitter_task.delay')
def test_publish_on_social_media_service(mock_publish_on_twitter_task):
    post = f.create_post(is_approved=True, posted_at='twitter', posted_time=None)
    assert post.is_posted is False
    services.publish_on_social_media()
    post.refresh_from_db()
    assert post.is_posted is True
    assert post.posted_time is not None
    mock_publish_on_twitter_task.assert_called_once_with(post.id)


@mock.patch('nexus.social_media.tasks.services.publish_on_twitter')
def test_publish_on_twitter_task(mock_publish_on_twitter):
    post = f.create_post()
    tasks.publish_on_twitter_task(post.id)
    mock_publish_on_twitter.assert_called_once_with(post.id)
