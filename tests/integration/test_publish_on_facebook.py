# Standard Library
from unittest.mock import ANY, patch

# Third Party Stuff
import pytest
from facebook import GraphAPI
from tests import factories as f

# nexus Stuff
from nexus.social_media.services import publish_on_facebook
from nexus.social_media.tasks import publish_on_social_media_task, publish_on_facebook_task

pytestmark = pytest.mark.django_db


@patch('nexus.social_media.services.get_fb_page_graph')
@patch('nexus.social_media.services.facebook.GraphAPI.put_photo')
@patch('nexus.social_media.services.facebook.GraphAPI.put_object')
def test_publish_on_facebook_service(mock_put_object, mock_put_photo, mock_page_graph):
    mock_page_graph.return_value = GraphAPI

    post = f.create_post(image=None)
    publish_on_facebook(post.id)
    mock_put_object.assert_called_with(
        parent_object=ANY, connection_name='feed', message=post.text
    )

    post = f.create_post(text=None)
    publish_on_facebook(post_id=post.id)
    mock_put_photo.assert_called_with(image=ANY)

    post = f.create_post()
    publish_on_facebook(post_id=post.id)
    mock_put_photo.assert_called_with(image=ANY, message=post.text)


@patch('nexus.social_media.services.settings')
@patch('nexus.social_media.tasks.services.tasks.publish_on_facebook_task.delay')
def test_publishing_limited_posts(mock_publish_on_facebook_task, mock_settings):
    mock_settings.MAX_POSTS_AT_ONCE = 2
    mock_settings.LIMIT_POSTS = False

    # Create an approved post with current time as scheduled time
    post = f.create_post(posted_at='fb', is_approved=True)
    publish_on_social_media_task()
    mock_publish_on_facebook_task.assert_called_once_with(post.id)
    post.refresh_from_db()
    assert post.is_posted is True
    assert post.posted_time is not None

    mock_settings.LIMIT_POSTS = True
    mock_publish_on_facebook_task.reset_mock()
    f.create_post(posted_at='fb', is_approved=True, n=3)
    publish_on_social_media_task()
    assert mock_publish_on_facebook_task.call_count == 2


@patch('nexus.social_media.tasks.services.publish_on_facebook')
def test_publish_on_facebook_task(mock_publish_on_facebook):
    post = f.create_post()
    publish_on_facebook_task(post.id)
    mock_publish_on_facebook.assert_called_once_with(post.id)
