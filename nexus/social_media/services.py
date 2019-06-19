# Third Party Stuff
import facebook
from django.conf import settings

# nexus Stuff
from nexus.base import exceptions
# Nexus Stuff
from nexus.social_media.models import Post


def get_fb_page_graph():
    graph = facebook.GraphAPI(settings.FB_USER_ACCESS_TOKEN)
    accounts = graph.get_object('me/accounts')['data']
    page_access_token = None
    for account in accounts:
        if account['id'] == settings.FB_PAGE_ID:
            page_access_token = account['access_token']
            break
    if page_access_token is None:
        raise exceptions.WrongArguments("Facebook Page access token could not be found")
    page_graph = facebook.GraphAPI(page_access_token)
    return page_graph


def post_to_facebook(post_id):
    post = Post.objects.get(pk=post_id)
    page_graph = get_fb_page_graph()
    if post.image:
        if post.text:
            page_graph.put_photo(image=post.image.file.open('rb'), message=post.text)
        else:
            page_graph.put_photo(image=post.image.file.open('rb'))
    elif post.text:
        page_graph.put_object(
            parent_object=settings.FB_PAGE_ID, connection_name='feed',  message=post.text
        )
