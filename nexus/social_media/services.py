# -*- coding: utf-8 -*-
# Third Party Stuff
import facebook
import requests
import tweepy
from django.conf import settings
from django.utils import timezone
from rest_framework import status

# nexus Stuff
from nexus.base import exceptions as exc
from nexus.social_media import tasks
from nexus.social_media.models import Post


def upload_image_to_linkedin(author, headers, post, linkedin_auth):
    """Upload image to linkedin for given post.

    :param author: Owner of the post to be used for response POST data.

    :param headers: HTTP headers required for successful HTTP request.

    :param post: Post model instance.

    :param linkedin_auth: LINKEDIN_AUTH object taken from settings.

    :returns: The value of asset provided all responses are successful.

    """
    post_data_assets = {
        'registerUploadRequest': {
            'recipes': [
                'urn:li:digitalmediaRecipe:feedshare-image'
            ],
            'owner': author,
            'serviceRelationships': [
                {
                    'relationshipType': 'OWNER',
                    'identifier': 'urn:li:userGeneratedContent'
                }
            ]
        }
    }

    # LinkedIn assets API endpoint
    api_url_assets = f'{settings.LINKEDIN_API_URL_BASE}assets?action=registerUpload'

    response_assets = requests.post(api_url_assets, json=post_data_assets,
                                    headers=headers)
    if response_assets.status_code == status.HTTP_200_OK:
        json_response_assets = response_assets.json()

        value = json_response_assets.get('value')
        upload_mechanism = value.get('uploadMechanism')
        upload_http_request = upload_mechanism.get('com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest')
        upload_url = upload_http_request.get('uploadUrl')

        asset = value.get('asset')

        response_upload_image = requests.post(upload_url,
                                              data=post.image.file.read(),
                                              headers={'Authorization': f"Bearer {linkedin_auth['access_token']}"})
        if response_upload_image.status_code == status.HTTP_201_CREATED:
            return asset
        else:
            check_and_raise_error_from_linkedin_response(response_upload_image)
    else:
        check_and_raise_error_from_linkedin_response(response_assets)


def publish_on_linkedin(post_id):
    """Function to post on linkedin

    :param post_id: UUID of the post instance to be posted.

    :returns: A valid HTTP response

    """
    linkedin_auth = settings.LINKEDIN_AUTH
    author = f"urn:li:organization:{linkedin_auth['organization_id']}"

    headers = {'X-Restli-Protocol-Version': '2.0.0',
               'Content-Type': 'application/json',
               'Authorization': f"Bearer {linkedin_auth['access_token']}"}

    # LinkedIn UGC(User Generated Content) API endpoint
    api_url_ugc = f'{settings.LINKEDIN_API_URL_BASE}ugcPosts'

    post = Post.objects.get(pk=post_id)

    post_data = {
        'author': author,
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary': {
                    'text': post.text
                },
                'shareMediaCategory': 'NONE'
            },
        },
        'visibility': {
            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
        },
    }

    if post.image:

        # asset is required to include the image in our post after successful uploading of image.
        asset = upload_image_to_linkedin(author, headers, post, linkedin_auth)

        specific_content = post_data.get('specificContent')
        share_content = specific_content.get('com.linkedin.ugc.ShareContent')

        image_media = [{
            'status': 'READY',
            'description': {
                'text': ''
            },
            'media': asset,
            'title': {
                'text': ''
            }
        }]
        share_content.update(shareMediaCategory='IMAGE',
                             media=image_media)
        image_response = requests.post(api_url_ugc, headers=headers,
                                       json=post_data)
        return image_response
    elif post.text:
        response = requests.post(api_url_ugc, headers=headers, json=post_data)
        return response


def check_and_raise_error_from_linkedin_response(response):
    """Function to perform appropriate action based on the linkedin response given.

    :param response: A valid HTTP response to perform suitable action.

    :raises WrongArguments: Exception raised when either a 400 or 404 response is provided.

    :raises NotAuthenticated: Exception raised when a 401 response is provided.

    :raises PermissionDenied: Exception raised when a 403 response is provided.

    :raises NotSupported: Exception raised when a 405 response is provided.

    :raises RequestValidationError: Exception raised when an unexpected response is provided.

    """
    status_code = response.status_code
    if (status_code != status.HTTP_201_CREATED) or (status_code != status.HTTP_200_OK):
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
        else:
            raise exc.RequestValidationError(error)


def get_twitter_api_object(TWITTER_OAUTH):
    """Function to generate a twitter API object.

    :param TWITTER_OAUTH: A dictionary having essential twitter oauth tokens viz.
    consumer_key, consumer_secret, access_key, access_secret.

    :returns: twitter API object.

    :raises WrongArguments: Exception, when invalid twitter oauth token(s) are provided.

    """
    try:
        auth = tweepy.OAuthHandler(TWITTER_OAUTH['consumer_key'], TWITTER_OAUTH['consumer_secret'])
        auth.set_access_token(TWITTER_OAUTH['access_key'], TWITTER_OAUTH['access_secret'])
        twitter_api = tweepy.API(auth)
        return twitter_api
    except tweepy.error.TweepError as exc_info:
        raise exc.WrongArguments(str(exc_info))


def publish_on_twitter(post_id):
    """Function to post on twitter.

    :param post_id: UUID of the post instance to be posted.

    :raises BadRequest: Exception, when unable to post to twitter using tweepy.

    """
    post = Post.objects.get(pk=post_id)
    twitter_api = get_twitter_api_object(settings.TWITTER_OAUTH)

    try:
        if post.image:
            filename = post.image.file.name
            twitter_api.update_with_media(filename=filename, status=post.text, file=post.image)
        elif post.text:
            twitter_api.update_status(status=post.text)
    except tweepy.error.TweepError as exc_info:
        raise exc.BadRequest(str(exc_info))


def get_fb_page_graph():
    graph = facebook.GraphAPI(settings.FB_USER_ACCESS_TOKEN)
    pages = graph.get_object('me/accounts')['data']
    page_access_token = None
    try:
        page_list = list(filter(lambda page: page['id'] == settings.FB_PAGE_ID, pages))
    except KeyError:
        raise exc.WrongArguments('No ID associated with FB_USER_ACCESS_TOKEN.')
    if not page_list:
        raise exc.WrongArguments('No matching ID in account data. Incorrect FB_PAGE_ID')
    page_access_token = page_list[0]['access_token']
    page_graph = facebook.GraphAPI(page_access_token)
    return page_graph


def publish_on_facebook(post_id):
    post = Post.objects.get(pk=post_id)
    page_graph = get_fb_page_graph()
    if post.image:
        if post.text:
            page_graph.put_photo(image=post.image.file.open('rb'),
                                 message=post.text)
        else:
            page_graph.put_photo(image=post.image.file.open('rb'))
    elif post.text:
        page_graph.put_object(
            parent_object=settings.FB_PAGE_ID, connection_name='feed', message=post.text
        )


def publish_on_social_media():
    posts = Post.objects.filter(is_approved=True, is_posted=False, scheduled_time__lte=timezone.now())

    if settings.LIMIT_POSTS is True and int(settings.MAX_POSTS_AT_ONCE) > 0:
        posts = posts[:int(settings.MAX_POSTS_AT_ONCE)]

    # Before performing the bulk update, here we are saving the IDs of posts along with there publishing platforms.
    # Because this queryset "posts" will get empty, after running the update query.
    post_id_and_platform = list(posts.values('id', 'posted_at'))

    Post.objects.filter(id__in=posts).update(is_posted=True, posted_time=timezone.now())

    for post in post_id_and_platform:
        if post['posted_at'] == 'fb':
            tasks.publish_on_facebook_task.delay(post['id'])
        elif post['posted_at'] == 'twitter':
            tasks.publish_on_twitter_task.delay(post['id'])
        elif post['posted_at'] == 'linkedin':
            tasks.publish_on_linkedin_task.delay(post['id'])
