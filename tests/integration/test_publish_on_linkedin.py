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

    # LinkedIn UGC(User Generated Content) API endpoint
    api_url_ugc = f"{settings.LINKEDIN_API_URL_BASE}ugcPosts"
    linkedin_auth = settings.LINKEDIN_AUTH
    author = f"urn:li:organization:{linkedin_auth['organization_id']}"
    headers = {'X-Restli-Protocol-Version': '2.0.0',
               'Content-Type': 'application/json',
               'Authorization': f"Bearer {linkedin_auth['access_token']}"}

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
            linkedin_auth,
            author,
            headers,
            post_data,
            )


@mock.patch('nexus.social_media.services.requests.post')
def test_publish_on_linkedin_without_image(mock_post, base_data):
    post, api_url_ugc, linkedin_auth, author, headers, post_data = base_data

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
    post, api_url_ugc, linkedin_auth, author, headers, post_data = base_data
    post = f.create_post()

    specific_content = post_data.get('specificContent')
    share_content = specific_content.get('com.linkedin.ugc.ShareContent')
    post_data_text = share_content.get('shareCommentary')
    post_data_text['text'] = post.text

    post_id = post.id
    post_instance = Post.objects.get(pk=post_id)
    mock_post.return_value = requests.Response()
    asset = mock.Mock()

    mock_upload_image_to_linkedin.return_value = asset

    specific_content = post_data.get('specificContent')
    share_content = specific_content.get('com.linkedin.ugc.ShareContent')

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

    share_content.update(shareMediaCategory='IMAGE', media=image_media)

    response_image = services.publish_on_linkedin(post_id)
    mock_upload_image_to_linkedin.assert_called_once_with(author,
                                                          headers,
                                                          post_instance,
                                                          linkedin_auth,
                                                          )
    mock_post.assert_called_once_with(api_url_ugc, headers=headers,
                                      json=post_data)
    assert isinstance(response_image, requests.Response)


@mock.patch('nexus.social_media.services.appropriate_response_action')
@mock.patch('nexus.social_media.services.requests.post')
@mock.patch('nexus.social_media.services.requests.Response.json')
def test_upload_image_to_linkedin(mock_json, mock_post, mock_appropriate_response_action, base_data):

    post, api_url_ugc, linkedin_auth, author, headers, post_data = base_data

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

    # When response_asset status code is not 200 as no status code has been set
    services.upload_image_to_linkedin(author,
                                      headers,
                                      post_instance,
                                      linkedin_auth,
                                      )
    mock_post.assert_called_once_with(api_url_assets, json=post_data_assets,
                                      headers=headers)
    mock_appropriate_response_action.assert_called_once_with(mock_post.return_value)

    # When response_asset status code is 200
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
    mock_appropriate_response_action.reset_mock()

    # When response_upload_image status code is not 201
    services.upload_image_to_linkedin(author,
                                      headers,
                                      post_instance,
                                      linkedin_auth,
                                      )
    # bring back the file pointer to starting postion as it's already read once
    # when the above call is made. So that reading it again in assertion
    # doesn't fail.
    post_instance.image.file.seek(0)
    assert mock_post.call_count == 2
    mock_post.assert_has_calls([
        mock.call(api_url_assets, json=post_data_assets, headers=headers),
        mock.call(upload_url, data=post_instance.image.file.read(),
                  headers={'Authorization': f"Bearer {linkedin_auth['access_token']}"})
    ])
    mock_appropriate_response_action.assert_called_once_with(mock_post.return_value)

    # When response_upload_image status code is 201
    return_values = [requests.Response(), requests.Response()]
    return_values[0].status_code = status.HTTP_200_OK
    return_values[1].status_code = status.HTTP_201_CREATED
    mock_post.side_effect = return_values

    post_instance.image.file.seek(0)
    mock_post.reset_mock()
    mock_appropriate_response_action.reset_mock()
    return_value = services.upload_image_to_linkedin(author,
                                                     headers,
                                                     post_instance,
                                                     linkedin_auth,
                                                     )
    post_instance.image.file.seek(0)
    assert mock_post.call_count == 2
    mock_post.assert_has_calls([
        mock.call(api_url_assets, json=post_data_assets, headers=headers),
        mock.call(upload_url, data=post_instance.image.file.read(),
                  headers={'Authorization': f"Bearer {linkedin_auth['access_token']}"})
    ])
    assert return_value == asset
    mock_appropriate_response_action.assert_not_called()


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

    with pytest.raises(exc.RequestValidationError) as excinfo:
        mock_response.status_code = status.HTTP_417_EXPECTATION_FAILED
        services.appropriate_response_action(mock_response)
    assert error in str(excinfo.value)


@mock.patch('nexus.social_media.tasks.services.appropriate_response_action')
@mock.patch('nexus.social_media.tasks.services.publish_on_linkedin')
def test_publish_on_linkedin_task(mock_publish_on_linkedin, mock_appropriate_response_action):
    post = f.create_post()
    tasks.publish_on_linkedin_task(post.id)
    # mock_publish_on_linkedin.return_value = requests.Response()
    mock_publish_on_linkedin.assert_called_once_with(post.id)
    mock_appropriate_response_action.assert_called_once_with(mock_publish_on_linkedin.return_value)


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
