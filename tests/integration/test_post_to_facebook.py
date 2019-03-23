# Standard Library
from unittest.mock import ANY, patch

# Third Party Stuff
import pytest
from facebook import GraphAPI
from tests import factories as f

# nexus Stuff
from nexus.social_media.services import post_to_facebook
from nexus.social_media.tasks import queue_posts

pytestmark = pytest.mark.django_db


@patch('nexus.social_media.services.get_fb_page_graph')
@patch('nexus.social_media.services.facebook.GraphAPI.put_photo')
@patch('nexus.social_media.services.facebook.GraphAPI.put_object')
def test_post_published(mock_put_object, mock_put_photo, mock_page_graph):
    mock_page_graph.return_value = GraphAPI

    post = f.create_post(image=None)
    post_to_facebook(post.id)
    mock_put_object.assert_called_with(
        parent_object=ANY, connection_name='feed', message=post.text
    )

    post = f.create_post(text=None)
    post_to_facebook(post_id=post.id)
    mock_put_photo.assert_called_with(image=ANY)

    post = f.create_post()
    post_to_facebook(post_id=post.id)
    mock_put_photo.assert_called_with(image=ANY, message=post.text)


@patch('nexus.social_media.tasks.settings')
@patch('nexus.social_media.tasks.post_to_facebook.delay')
def test_queue_posts_task(mock_delay, mock_settings):
    mock_settings.MAX_POSTS_AT_ONCE = 2
    mock_settings.LIMIT_POSTS = False

    # Create an approved post with current time as scheduled time
    post = f.create_post(posted_at='fb', is_approved=True)
    queue_posts()
    mock_delay.assert_called_once_with(post.id)
    post.refresh_from_db()
    assert post.is_posted is True
    assert post.posted_time is not None

    mock_settings.LIMIT_POSTS = True
    mock_delay.reset_mock()
    f.create_post(posted_at='fb', is_approved=True, n=3)
    queue_posts()
    assert mock_delay.call_count == 2
