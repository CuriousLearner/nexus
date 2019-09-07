# -*- coding: utf-8 -*-
# Standard Library
from unittest.mock import ANY, patch

# Third Party Stuff
import pytest
from facebook import GraphAPI
from tests import factories as f

# nexus Stuff
from nexus.base import exceptions
from nexus.social_media.services import get_fb_page_graph, publish_on_facebook
from nexus.social_media.tasks import publish_on_facebook_task, publish_on_social_media_task

pytestmark = pytest.mark.django_db


@patch('nexus.social_media.services.settings')
@patch('nexus.social_media.services.facebook.GraphAPI', autospec=True)
def test_get_fb_page_graph(mock_graph_api, mock_settings):
    mock_settings.FB_USER_ACCESS_TOKEN = 'token123'
    mock_settings.FB_PAGE_ID = '012345'
    accounts_data = {'data': [{'access_token': 'pagetoken123'}]}
    mock_graph_api.return_value.get_object.return_value = accounts_data

    # Data not containing ID key
    with pytest.raises(exceptions.WrongArguments) as exc:
        get_fb_page_graph()
    assert 'No ID' in str(exc.value)
    mock_graph_api.assert_called_with('token123')

    # Data not containing matching ID
    accounts_data['data'][0]['id'] = '000000'
    with pytest.raises(exceptions.WrongArguments) as exc:
        get_fb_page_graph()
    assert 'No matching ID' in str(exc.value)

    # Data containing matching ID
    accounts_data['data'][0]['id'] = '012345'
    get_fb_page_graph()
    mock_graph_api.assert_called_with('pagetoken123')


@patch('nexus.social_media.services.get_fb_page_graph', autospec=GraphAPI)
def test_publish_on_facebook_service(mock_page_graph):
    post = f.create_post(image=None)
    publish_on_facebook(post.id)
    mock_page_graph.return_value.put_object.assert_called_with(
        parent_object=ANY, connection_name='feed', message=post.text
    )

    post = f.create_post(text=None)
    publish_on_facebook(post_id=post.id)
    mock_page_graph.return_value.put_photo.assert_called_with(image=ANY)

    post = f.create_post()
    publish_on_facebook(post_id=post.id)
    mock_page_graph.return_value.put_photo.assert_called_with(
        image=ANY, message=post.text
    )


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
