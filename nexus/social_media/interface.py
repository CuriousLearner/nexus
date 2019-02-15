# Standard Library
import os

# Third Party Stuff
import facebook
from dotenv import load_dotenv
from celery.decorators import task

# Nexus Stuff
from nexus.social_media.models import Post

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


user_access_token = os.getenv('FB_USER_ACCESS_TOKEN')
page_id = os.getenv('FB_PAGE_ID')


@task
def post_to_facebook(id):
    post = Post.objects.get(pk=id)
    graph = facebook.GraphAPI(user_access_token)
    accounts = graph.get_object('me/accounts')['data']
    page_access_token = None
    for account in accounts:
        if account['id'] == page_id:
            page_access_token = account['access_token']
            break
    if page_access_token is None:
        print("Sorry, no page found with given user and page_id combination")
        return
    page_graph = facebook.GraphAPI(page_access_token)
    if post.image:
        if post.text:
            page_graph.put_photo(image=post.image.file.open('rb'), message=post.text)
        else:
            page_graph.put_photo(image=post.image.file.open('rb'))
    elif post.text:
        page_graph.put_object(page_id, 'feed',  message=post.text)
