# Standard Library
import json
from unittest import mock

# Third Party Stuff
import pytest
import requests
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from tests import factories as f
from tests import utils as u

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media import services, tasks
from nexus.social_media.models import Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def base_data(client):
    post = {
        'text': 'Announcement!',
        'posted_at': 'linkedin',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }

    api_url_base = 'https://api.linkedin.com/v2/'
    api_url_ugc = f"{api_url_base}ugcPosts"
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
                    "text": post.get('text')
                },
                "shareMediaCategory": "NONE"
            },
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')

    response = client.json.post(url, json.dumps(post))

    return (post,
            api_url_base,
            api_url_ugc,
            linkedin,
            author,
            headers,
            post_data,
            response,
            client,)


@pytest.fixture
def base_data_for_image(base_data, client):
    post, api_url_base, api_url_ugc, linkedin, author, headers, post_data, response, client = base_data
    post_id = response.data['id']
    image = u.create_image(None, 'avatar.png')
    image = SimpleUploadedFile('front.png', image.getvalue())
    url = reverse('posts-upload-image', kwargs={'pk': post_id})
    client.post(url, {'image': image}, format='multipart')
    # removes client from the base_data tuple and return the remaining element
    return tuple(x for x in base_data if x != client)


@mock.patch('nexus.social_media.services.requests.post')
def test_post_to_linkedin_without_image(mock_post, base_data):
    post, api_url_base, api_url_ugc, linkedin, author, headers, post_data, response, client = base_data
    assert response.status_code == status.HTTP_201_CREATED

    expected_keys = {'text', 'posted_at', 'scheduled_time'}
    assert expected_keys.issubset(response.data.keys())

    post_id = response.data['id']

    mock_post.return_value = requests.Response()

    # check post only with text
    response = services.post_to_linkedin(post_id)
    mock_post.assert_called_once_with(api_url_ugc, headers=headers,
                                      json=post_data)
    assert isinstance(response, requests.Response)


@mock.patch('nexus.social_media.services.requests.post')
@mock.patch('nexus.social_media.services.upload_image_to_linkedin')
def test_post_to_linkedin_with_image(mock_upload_image_to_linkedin,
                                     mock_post, base_data_for_image):
    post, api_url_base, api_url_ugc, linkedin, author, headers, post_data, response = base_data_for_image

    post_id = response.data['id']
    post_instance = Post.objects.get(pk=post_id)
    mock_post.return_value = requests.Response()
    response_upload_image = requests.Response()
    asset = mock.Mock()

    mock_upload_image_to_linkedin.return_value = (response_upload_image, asset)

    # if response_upload_image doesn't have a 201 status code
    unsuccessful_response = services.post_to_linkedin(post_id)
    mock_upload_image_to_linkedin.assert_called_once_with(author,
                                                          headers,
                                                          post_instance,
                                                          api_url_base,
                                                          linkedin,)
    mock_post.assert_not_called()
    assert isinstance(unsuccessful_response, requests.Response)

    # if response_upload_image_have a 201 status code
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

    shareContent.update(shareMediaCategory='IMAGE',
                        media=image_media)

    mock_upload_image_to_linkedin.reset_mock()
    response_image = services.post_to_linkedin(post_id)
    mock_upload_image_to_linkedin.assert_called_once_with(author,
                                                          headers,
                                                          post_instance,
                                                          api_url_base,
                                                          linkedin,)
    mock_post.assert_called_once_with(api_url_ugc, headers=headers,
                                      json=post_data)
    assert isinstance(response_image, requests.Response)


@mock.patch('nexus.social_media.services.requests.post')
@mock.patch('nexus.social_media.services.requests.Response.json')
def test_upload_image_to_linkedin(mock_json, mock_post, base_data_for_image):

    post, api_url_base, api_url_ugc, linkedin, author, headers, post_data, response = base_data_for_image

    post_id = response.data['id']
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

    api_url_assets = f"{api_url_base}assets?action=registerUpload"
    mock_post.return_value = requests.Response()

    # When status code is not 200
    response_upload_image = services.upload_image_to_linkedin(author,
                                                              headers,
                                                              post_instance,
                                                              api_url_base,
                                                              linkedin,)
    mock_post.assert_called_once_with(api_url_assets, json=post_data_assets,
                                      headers=headers)
    assert isinstance(response_upload_image, tuple)
    assert len(response_upload_image) == 2
    assert isinstance(response_upload_image[0], requests.Response)
    assert isinstance(response_upload_image[1], type(None))

    # When status code is 200
    uploadUrl = mock.Mock()
    asset = mock.Mock()
    mock_post.return_value.status_code = status.HTTP_200_OK
    mock_json.return_value = {
        "value": {
            "uploadMechanism": {
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                    "headers": {},
                    "uploadUrl": uploadUrl,
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
                                                              api_url_base,
                                                              linkedin,)
    # bring back the file pointer to starting postion as it's already read once
    # when the above call is made. So that reading it again in assertion
    # doesn't fail.
    post_instance.image.file.seek(0)
    assert mock_post.call_count == 2
    mock_post.assert_has_calls([
        mock.call(api_url_assets, json=post_data_assets, headers=headers),
        mock.call(uploadUrl, data=post_instance.image.file.read(),
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


@mock.patch('nexus.social_media.services.timezone')
@mock.patch('nexus.social_media.services.appropriate_response_action')
@mock.patch('nexus.social_media.services.post_to_linkedin')
def test_publish_post_service(mock_post_to_linkedin,
                              mock_appropriate_response_action,
                              mock_timezone,
                              client):
    core_organizer = f.create_user(is_core_organizer=True)
    client.login(user=core_organizer)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'linkedin',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }

    response = client.json.post(url, json.dumps(post))
    post_id = response.data['id']

    url = reverse('posts-approve', kwargs={'pk': post_id})
    client.post(url)

    post_instance = Post.objects.get(pk=post_id)
    assert post_instance.is_approved

    current_time = timezone.now()

    mock_post_to_linkedin.return_value = requests.Response()
    mock_timezone.now.return_value = current_time

    services.publish_post_service()

    post_instance = Post.objects.get(pk=post_id)

    assert post_instance.posted_time == current_time
    assert post_instance.is_posted
    mock_post_to_linkedin.assert_called_once_with(post_instance.id)
    mock_appropriate_response_action.assert_called_once_with(mock_post_to_linkedin.return_value)


@mock.patch('nexus.social_media.tasks.publish_post_service')
def test_publish_post_task(mock_publish_post_service):
    tasks.publish_posts_to_social_media()
    mock_publish_post_service.assert_called_once()
