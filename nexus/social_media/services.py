# Standard Library
from datetime import datetime

# Third Party Stuff
import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status
import facebook

# nexus Stuff
from nexus.social_media import tasks
from nexus.base import exceptions as exc
from nexus.social_media.models import Post


def upload_image_to_linkedin(author, headers, post, linkedin):
    """Upload image to linkedin for given post.

    :param author: Owner of the post to be used for response POST data.

    :param headers: HTTP headers required for successful HTTP request.

    :param post: Post model instance.

    :param linkedin: LINKEDIN_AUTH object taken from settings.

    :returns: A valid HTTP response.

    """
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

    response_assets = requests.post(api_url_assets, json=post_data_assets,
                                    headers=headers)
    if response_assets.status_code == status.HTTP_200_OK:
        json_response_assets = response_assets.json()
        upload_url = json_response_assets.get('value')\
                                         .get('uploadMechanism')\
                                         .get('com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest')\
                                         .get('uploadUrl')

        asset = json_response_assets.get('value').get('asset')
        response_upload_image = requests.post(upload_url,
                                              data=post.image.file.read(),
                                              headers={'Authorization': f"Bearer {linkedin['access_token']}"})
        return (response_upload_image, asset)
    else:
        return (response_assets, None)


def publish_on_linkedin(post_id):
    """Function to post on linkedin

    :param post_id: UUID of the post instance to be posted.

    :returns: A valid HTTP response

    """
    linkedin = settings.LINKEDIN_AUTH
    author = f"urn:li:organization:{linkedin['organization_id']}"

    headers = {'X-Restli-Protocol-Version': '2.0.0',
               'Content-Type': 'application/json',
               'Authorization': f"Bearer {linkedin['access_token']}"}

    api_url_ugc = f"{settings.LINKEDIN_API_URL_BASE}ugcPosts"

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


def appropriate_response_action(response):
    """Function to perform appropriate action based on the response given.

    :param response: A valid HTTP response to perform suitable action.

    :raises WrongArguments: Exception raised when either a 400 or 404 response is provided.

    :raises NotAuthenticated: Exception raised when a 401 response is provided.

    :raises PermissionDenied: Exception raised when a 403 response is provided.

    :raises NotSupported: Exception raised when a 405 response is provided.

    """
    status_code = response.status_code
    if status_code != status.HTTP_201_CREATED:
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


def get_fb_page_graph():
    graph = facebook.GraphAPI(settings.FB_USER_ACCESS_TOKEN)
    pages = graph.get_object('me/accounts')['data']
    page_access_token = None
    page_list = list(filter(lambda page: page['id'] == settings.FB_PAGE_ID, pages))
    if not page_list:
        raise exc.WrongArguments("Facebook Page access token could not be found")
    page_access_token = page_list[0]['access_token']
    page_graph = facebook.GraphAPI(page_access_token)
    return page_graph


def publish_on_facebook(post_id):
    post = Post.objects.get(pk=post_id)
    page_graph = get_fb_page_graph()
    if post.image:
        if post.text:
            page_graph.put_photo(image=post.image.file.open('rb'), message=post.text)
        else:
            page_graph.put_photo(image=post.image.file.open('rb'))
    elif post.text:
        page_graph.put_object(
            parent_object=settings.FB_PAGE_ID, connection_name='feed', message=post.text
        )


def publish_on_social_media():
    if settings.LIMIT_POSTS is True and int(settings.MAX_POSTS_AT_ONCE) > 0:
        posts = Post.objects.filter(
            is_approved=True, is_posted=False, scheduled_time__lte=datetime.now()
        )[:int(settings.MAX_POSTS_AT_ONCE)]
    else:
        posts = Post.objects.filter(
            is_approved=True, is_posted=False, scheduled_time__lte=datetime.now()
        )

    # Before bulk update, saving the IDs of posts along with there publishing platforms.
    post_platform = {}
    for post in posts:
        post_platform.update({post.id: post.posted_at})

    if settings.LIMIT_POSTS is True and int(settings.MAX_POSTS_AT_ONCE) > 0:
        Post.objects.filter(id__in=posts).update(is_posted=True, posted_time=timezone.now())
    else:
        posts.update(is_posted=True, posted_time=timezone.now())

    for post_id in post_platform:
        if post_platform[post_id] == 'fb':
            tasks.publish_on_facebook_task.s(post_id).apply_async()
        elif post_platform[post_id] == 'linkedin':
            tasks.publish_on_linkedin_task.s(post_id).apply_async()
