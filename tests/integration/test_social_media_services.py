# Standard Library
import json
from unittest import mock

# Third Party Stuff
import pytest
import tweepy
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from tests import factories as f
from tests import utils as u

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media import services
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

    mock_api.side_effect = tweepy.error.TweepError('TweepError: Invalid Twitter OAuth Token(s).')
    try:
        services.get_twitter_api_object(settings.TWITTER_OAUTH)
        assert False is True
    except exc.WrongArguments:
        assert True is True


@mock.patch('nexus.social_media.services.get_twitter_api_object')
def test_publish_posts_to_twitter_service(mock_get_twitter_api_object, client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'twitter',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }

    response = client.json.post(url, json.dumps(post))
    post_id = response.data['id']

    mock_get_twitter_api_object.return_value = tweepy.api

    # Check post only with text
    with mock.patch('nexus.social_media.services.tweepy.api.update_status') as mock_update_status:
        services.publish_posts_to_twitter(post_id)
        mock_get_twitter_api_object.assert_called_once_with(settings.TWITTER_OAUTH)
        mock_update_status.assert_called_once_with(status=post['text'])

    # Check post with image
    image = u.create_image(None, 'avatar.png')
    image = SimpleUploadedFile('front.png', image.getvalue())
    url = reverse('posts-upload-image', kwargs={'pk': post_id})
    client.post(url, {'image': image}, format='multipart')

    post_instance = Post.objects.get(pk=post_id)
    image_file = post_instance.image.file.name

    with mock.patch('nexus.social_media.services.tweepy.api.update_with_media') as mock_update_with_media:
        services.publish_posts_to_twitter(post_id)
        mock_update_with_media.assert_called_once_with(
            filename=image_file, status=post['text'], file=post_instance.image
        )

        # Raising a TweepError
        mock_update_with_media.side_effect = tweepy.error.TweepError('TweepError: Unable to post to twitter')
        try:
            services.publish_posts_to_twitter(post_id)
            assert True is False
        except exc.BadRequest:
            assert True is True


@mock.patch('nexus.social_media.services.publish_posts_to_twitter')
def test_publish_posts_to_social_media_service(mock_publish_posts_to_twitter, client):
    core_organizer = f.create_user(is_core_organizer=True)
    client.login(user=core_organizer)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'twitter',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }

    response = client.json.post(url, json.dumps(post))
    post_id = response.data['id']
    post_instance = Post.objects.get(pk=post_id)

    url = reverse('posts-approve', kwargs={'pk': post_id})
    client.post(url)

    services.publish_posts_to_social_media()
    mock_publish_posts_to_twitter.assert_called_once_with(post_instance.id)
