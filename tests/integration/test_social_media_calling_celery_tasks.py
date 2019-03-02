# Standard Stuff
import json

# Third Party Stuff
import pytest
from unittest import mock
from django.urls import reverse

# nexus Stuff
from tests import factories as f
from nexus.social_media.models import Post

pytestmark = pytest.mark.django_db


def test_calling_twitter_celery_task(client):
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

    with mock.patch('nexus.social_media.api.task_to_post_to_twitter.delay') as mock_delay:
        url = reverse('posts-approve', kwargs={'pk': post_id})
        client.post(url)
        assert mock_delay.assert_called_once_with(post_instance.id) is None
