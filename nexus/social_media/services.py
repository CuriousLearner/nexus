# -*- coding: utf-8 -*-
# Third Party Stuff
import facebook
from django.conf import settings

# nexus Stuff
from nexus.base import exceptions
# Nexus Stuff
from nexus.social_media.models import Post


def get_fb_page_graph():
    graph = facebook.GraphAPI(settings.FB_USER_ACCESS_TOKEN)
    pages = graph.get_object('me/accounts')['data']
    page_access_token = None
    try:
        page_list = list(filter(lambda page: page['id'] == settings.FB_PAGE_ID, pages))
    except KeyError:
        raise exceptions.WrongArguments('No ID associated with FB_USER_ACCESS_TOKEN.')
    if not page_list:
        raise exceptions.WrongArguments('No matching ID in account data. Incorrect FB_PAGE_ID')
    page_access_token = page_list[0]['access_token']
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
