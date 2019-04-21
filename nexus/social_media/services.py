# Third Party Stuff
import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media.models import Post


def update_post_object(post):
    """Update post instance after the post is published.
    :param post: Post model instance.
    """
    post.posted_time = timezone.now()
    post.is_posted = True
    post.save()


def upload_image_to_linkedin(author, headers, post, api_url_base, linkedin):
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

    response_assets = requests.post(api_url_assets, json=post_data_assets,
                                    headers=headers)
    if response_assets.status_code == status.HTTP_200_OK:
        json_response_assets = response_assets.json()
        uploadUrl = json_response_assets.get('value')\
                                        .get('uploadMechanism')\
                                        .get('com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest')\
                                        .get('uploadUrl')

        asset = json_response_assets.get('value').get('asset')
        with open(post.image.file.name, 'rb') as f:
            response_upload_image = requests.post(uploadUrl, data=f.read(),
                                                  headers={'Authorization': f"Bearer {linkedin['access_token']}"})
        return (response_upload_image, asset)
    else:
        return (response_assets, None)


def post_to_linkedin(post_id):
    """Function to post on linkedin
    :param post_id: UUID of the post instance to be posted.
    :returns: A valid HTTP response
    """
    linkedin = settings.LINKEDIN_AUTH
    author = f"urn:li:organization:{linkedin['organization_id']}"

    headers = {'X-Restli-Protocol-Version': '2.0.0',
               'Content-Type': 'application/json',
               'Authorization': f"Bearer {linkedin['access_token']}"}

    api_url_base = 'https://api.linkedin.com/v2/'

    api_url_ugc = f"{api_url_base}ugcPosts"

    post = Post.objects.get(pk=post_id)

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

    if post.image:
        response_upload_image, asset = upload_image_to_linkedin(author,
                                                                headers,
                                                                post,
                                                                api_url_base,
                                                                linkedin)

        if response_upload_image.status_code == status.HTTP_201_CREATED:
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
            image_response = requests.post(api_url_ugc, headers=headers,
                                           json=post_data)
            return image_response
        else:
            return response_upload_image
    elif post.text:
        response = requests.post(api_url_ugc, headers=headers, json=post_data)
        return response


def appropriate_response_action(response, post):
    """Function to perform appropriate action based on the response given.
    :param response: A valid HTTP response to perform suitable action.
    :param post: Post instance which is to be updated when a succesfull response is provided.
    :raises WrongArguments: Exception raised when either a 400 or 404 response is provided.
    :raises NotAuthenticated: Exception raised when a 401 response is provided.
    :raises PermissionDenied: Exception raised when a 403 response is provided.
    :raises NotSupported: Exception raised when a 405 response is provided.
    """
    status_code = response.status_code
    if status_code == status.HTTP_201_CREATED:
        update_post_object(post)
    elif status_code != status.HTTP_201_CREATED:
        json_response = response.json()
        error = f"LinkedIn error: {json_response['message']}"
        if status_code == status.HTTP_400_BAD_REQUEST:
            raise exc.WrongArguments(error)
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            raise exc.NotAuthenticated(error)
        elif status_code == status.HTTP_403_FORBIDDEN:
            raise exc.PermissionDenied(error)
        elif status_code == status.HTTP_404_NOT_FOUND:
            raise exc.WrongArguments(error)
        elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            raise exc.NotSupported(error)


def publish_post_service():
    """Function to publish social media post"""
    posts = Post.objects.filter(
        is_approved=True, is_posted=False, scheduled_time__lte=timezone.now()
    )
    for post in posts:
        if post.posted_at == 'linkedin':
            response = post_to_linkedin(post.id)
            appropriate_response_action(response, post)
