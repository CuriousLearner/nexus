# Third Party Stuff
import facebook
from nexus.celery import app

# Nexus Stuff
from nexus.social_media.models import Post
from nexus.base import response
from settings.common import FB_USER_ACCESS_TOKEN, FB_PAGE_ID


@app.task
def post_to_facebook(post_id):
    post = Post.objects.get(pk=post_id)
    graph = facebook.GraphAPI(FB_USER_ACCESS_TOKEN)
    accounts = graph.get_object('me/accounts')['data']
    page_access_token = None
    for account in accounts:
        if account['id'] == FB_PAGE_ID:
            page_access_token = account['access_token']
            break
    if page_access_token is None:
        return response.BadRequest({'error_message': 'No page found with given user id and page combination'})
    page_graph = facebook.GraphAPI(page_access_token)
    if post.image:
        if post.text:
            page_graph.put_photo(image=post.image.file.open('rb'), message=post.text)
        else:
            page_graph.put_photo(image=post.image.file.open('rb'))
    elif post.text:
        page_graph.put_object(FB_PAGE_ID, 'feed',  message=post.text)
