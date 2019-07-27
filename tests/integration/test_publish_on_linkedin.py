# Standard Library
from unittest import mock

# Third Party Stuff
import pytest
import requests
from django.conf import settings
from rest_framework import status
from tests import factories as f

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media import services, tasks
from nexus.social_media.models import Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def base_data(client):
    post = f.create_post(image=None)
    api_url_ugc = f"{settings.LINKEDIN_API_URL_BASE}ugcPosts"
    linkedin = settings.LINKEDIN_AUTH
    author = f"urn:li:organization:{linkedin['organization_id']}"
    headers = {'X-Restli-Protocol-Version': '2.0.0',
               'Content-Type': 'application/json',
               'Authorization': f"Bearer {linkedin['access_token']}"}

    post_data = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post.text
                },
                "shareMediaCategory": "NONE"
            },
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    return (post,
            api_url_ugc,
            linkedin,
            author,
            headers,
            post_data,)


@mock.patch('nexus.social_media.services.requests.post')
def test_publish_on_linkedin_without_image(mock_post, base_data):
    post, api_url_ugc, linkedin, author, headers, post_data = base_data

    post_id = post.id

    mock_post.return_value = requests.Response()

    # check post only with text
    response = services.publish_on_linkedin(post_id)
    mock_post.assert_called_once_with(api_url_ugc, headers=headers,
                                      json=post_data)
    assert isinstance(response, requests.Response)


@mock.patch('nexus.social_media.services.requests.post')
@mock.patch('nexus.social_media.services.upload_image_to_linkedin')
def test_publish_on_linkedin_with_image(mock_upload_image_to_linkedin, mock_post, base_data):
    post, api_url_ugc, linkedin, author, headers, post_data = base_data
    post = f.create_post()
    post_data_text = post_data.get('specificContent')\
                              .get('com.linkedin.ugc.ShareContent')\
                              .get('shareCommentary')
    post_data_text['text'] = post.text

    post_id = post.id
    post_instance = Post.objects.get(pk=post_id)
    mock_post.return_value = requests.Response()
    response_upload_image = requests.Response()
    asset = mock.Mock()

    mock_upload_image_to_linkedin.return_value = (response_upload_image, asset)

    # if response_upload_image doesn't have a 201 status code
    unsuccessful_response = services.publish_on_linkedin(post_id)
    mock_upload_image_to_linkedin.assert_called_once_with(author,
                                                          headers,
                                                          post_instance,
                                                          linkedin,)
    mock_post.assert_not_called()
    assert isinstance(unsuccessful_response, requests.Response)

    # if response_upload_image have a 201 status code
    response_upload_image.status_code = status.HTTP_201_CREATED

    shareContent = post_data.get('specificContent')\
                            .get('com.linkedin.ugc.ShareContent')
    image_media = [{
        "status": "READY",
        "description": {
            "text": ""
        },
        "media": asset,
        "title": {
            "text": ""
        }
    }]

    shareContent.update(shareMediaCategory='IMAGE', media=image_media)

    mock_upload_image_to_linkedin.reset_mock()
    response_image = services.publish_on_linkedin(post_id)
    mock_upload_image_to_linkedin.assert_called_once_with(author,
                                                          headers,
                                                          post_instance,
                                                          linkedin,)
    mock_post.assert_called_once_with(api_url_ugc, headers=headers,
                                      json=post_data)
    assert isinstance(response_image, requests.Response)


@mock.patch('nexus.social_media.services.requests.post')
@mock.patch('nexus.social_media.services.requests.Response.json')
def test_upload_image_to_linkedin(mock_json, mock_post, base_data):

    post, api_url_ugc, linkedin, author, headers, post_data = base_data

    post = f.create_post()
    post_id = post.id
    post_instance = Post.objects.get(pk=post_id)

    post_data_assets = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": author,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    api_url_assets = f"{settings.LINKEDIN_API_URL_BASE}assets?action=registerUpload"
    mock_post.return_value = requests.Response()

    # When status code is not 200
    response_upload_image = services.upload_image_to_linkedin(author,
                                                              headers,
                                                              post_instance,
                                                              linkedin,)
    mock_post.assert_called_once_with(api_url_assets, json=post_data_assets,
                                      headers=headers)
    assert isinstance(response_upload_image, tuple)
    assert len(response_upload_image) == 2
    assert isinstance(response_upload_image[0], requests.Response)
    assert isinstance(response_upload_image[1], type(None))

    # When status code is 200
    upload_url = mock.Mock()
    asset = mock.Mock()
    mock_post.return_value.status_code = status.HTTP_200_OK
    mock_json.return_value = {
        "value": {
            "uploadMechanism": {
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                    "headers": {},
                    "uploadUrl": upload_url,
                }
            },
            "mediaArtifact": mock.Mock(),
            "asset": asset
        }
    }
    mock_post.reset_mock()
    response_upload_image = services.upload_image_to_linkedin(author,
                                                              headers,
                                                              post_instance,
                                                              linkedin,)
    # bring back the file pointer to starting postion as it's already read once
    # when the above call is made. So that reading it again in assertion
    # doesn't fail.
    post_instance.image.file.seek(0)
    assert mock_post.call_count == 2
    mock_post.assert_has_calls([
        mock.call(api_url_assets, json=post_data_assets, headers=headers),
        mock.call(upload_url, data=post_instance.image.file.read(),
                  headers={'Authorization': f"Bearer {linkedin['access_token']}"})
    ])
    assert isinstance(response_upload_image, tuple)
    assert len(response_upload_image) == 2
    assert isinstance(response_upload_image[0], requests.Response)
    assert response_upload_image[1] == asset


@mock.patch('nexus.social_media.services.requests.Response')
def test_appropriate_response_action(mock_response):
    mock_response.json.return_value = {
        "message": "Error!",
        "serviceErrorCode": mock.Mock(),
        "status": mock.Mock()
    }
    error = f"LinkedIn error: {mock_response.json.return_value['message']}"
    with pytest.raises(exc.WrongArguments) as excinfo:
        mock_response.status_code = status.HTTP_400_BAD_REQUEST
        services.appropriate_response_action(mock_response)
    assert error in str(excinfo.value)

    with pytest.raises(exc.WrongArguments) as excinfo:
        mock_response.status_code = status.HTTP_404_NOT_FOUND
        services.appropriate_response_action(mock_response)
    assert error in str(excinfo.value)

    with pytest.raises(exc.NotAuthenticated) as excinfo:
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED
        services.appropriate_response_action(mock_response)
    assert error in str(excinfo.value)

    with pytest.raises(exc.PermissionDenied) as excinfo:
        mock_response.status_code = status.HTTP_403_FORBIDDEN
        services.appropriate_response_action(mock_response)
    assert error in str(excinfo.value)

    with pytest.raises(exc.NotSupported) as excinfo:
        mock_response.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        services.appropriate_response_action(mock_response)
    assert error in str(excinfo.value)


@mock.patch('nexus.social_media.tasks.services.appropriate_response_action')
@mock.patch('nexus.social_media.tasks.services.publish_on_linkedin')
def test_publish_on_linkedin_task(mock_publish_on_linkedin, mock_appropriate_response_action):
    post = f.create_post()
    tasks.publish_on_linkedin_task(post.id)
    # mock_publish_on_linkedin.return_value = requests.Response()
    mock_publish_on_linkedin.assert_called_once_with(post.id)
    mock_appropriate_response_action.assert_called_once()


@mock.patch('nexus.social_media.services.tasks.publish_on_linkedin_task.delay')
def test_publish_on_social_media_service(mock_publish_on_linkedin_task):
    post = f.create_post(is_approved=True, posted_at='linkedin',
                         posted_time=None)
    assert post.is_posted is False
    services.publish_on_social_media()
    post.refresh_from_db()
    assert post.is_posted is True
    assert post.posted_time is not None
    mock_publish_on_linkedin_task.assert_called_once_with(post.id)
