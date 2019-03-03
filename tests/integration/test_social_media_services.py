# Standard Stuff
import json

# Third Party Stuff
import pytest
import tweepy
from unittest import mock
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile


# nexus Stuff
from tests import utils as u
from tests import factories as f
from nexus.social_media import tasks
from nexus.social_media import services
from nexus.base import exceptions as exc
from nexus.social_media.models import Post
from settings.development import TWITTER_OAUTH


pytestmark = pytest.mark.django_db


def test_update_post_object(client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'twitter',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }

    response = client.json.post(url, json.dumps(post))
    post_instance = Post.objects.get(pk=response.data['id'])

    assert post_instance.is_posted is False
    assert post_instance.posted_time is None

    services.update_post_object(post_instance)

    assert post_instance.is_posted is True
    assert post_instance.posted_time.date() == timezone.now().date()


def test_get_twitter_api_object():
    with mock.patch('nexus.social_media.services.tweepy.OAuthHandler') as mock_oauthhandler:
        mock_oauthhandler.return_value = tweepy.OAuthHandler

        with mock.patch('nexus.social_media.services.tweepy.OAuthHandler.set_access_token') as mock_set_access_token:

            with mock.patch('nexus.social_media.services.tweepy.API') as mock_api:

                services.get_twitter_api_object(TWITTER_OAUTH)

                assert mock_oauthhandler.assert_called_once_with(
                    TWITTER_OAUTH['consumer_key'], TWITTER_OAUTH['consumer_secret']) is None
                assert mock_set_access_token.assert_called_once_with(
                    TWITTER_OAUTH['access_key'], TWITTER_OAUTH['access_secret']) is None
                assert mock_api.assert_called_once_with(mock_oauthhandler) is None

                mock_api.side_effect = tweepy.error.TweepError('TweepError: Invalid Twitter OAuth Token(s).')
                try:
                    services.get_twitter_api_object(TWITTER_OAUTH)
                    assert False is True
                except exc.WrongArguments:
                    assert True is True


def test_post_to_twitter(client):
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

    with mock.patch('nexus.social_media.services.get_twitter_api_object') as mock_get_twitter_api_object:

        mock_get_twitter_api_object.return_value = tweepy.api

        # Post only with text
        with mock.patch('nexus.social_media.services.tweepy.api.update_status') as mock_update_status:
            services.post_to_twitter(post_id)
            assert mock_get_twitter_api_object.assert_called_once_with(TWITTER_OAUTH) is None
            assert mock_update_status.assert_called_once_with(status=post['text']) is None

        # Post with text and image
        image = u.create_image(None, 'avatar.png')
        image = SimpleUploadedFile('front.png', image.getvalue())
        url = reverse('posts-upload-image', kwargs={'pk': post_id})
        client.post(url, {'image': image}, format='multipart')

        post_instance = Post.objects.get(pk=post_id)
        image_file = post_instance.image.file.name

        with mock.patch('nexus.social_media.services.tweepy.api.update_with_media') as mock_update_with_media:
            services.post_to_twitter(post_id)
            assert mock_update_with_media.assert_called_once_with(
                filename=image_file, status=post['text'], file=post_instance.image) is None

        # Post only with image
        post_instance.text = None
        post_instance.save()
        with mock.patch('nexus.social_media.services.tweepy.api.update_with_media') as mock_update_with_media:
            services.post_to_twitter(post_id)
            assert mock_update_with_media.assert_called_once_with(filename=image_file, file=post_instance.image) is None

            # Raising a TweepError
            mock_update_with_media.side_effect = tweepy.error.TweepError('TweepError: Unable to post to twitter')
            try:
                services.post_to_twitter(post_id)
                assert True is False
            except exc.BadRequest:
                assert True is True


@mock.patch('nexus.social_media.services.post_to_twitter')
def test_publish_posts(mock_post_to_twitter, client):
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

    services.publish_posts()
    assert mock_post_to_twitter.assert_called_once_with(post_instance.id) is None


@mock.patch('nexus.social_media.tasks.publish_posts')
def test_calling_queue_posts(mock_publish_posts):
    tasks.queue_posts()
    assert mock_publish_posts.assert_called_once_with() is None
