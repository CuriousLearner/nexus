# Third Party Stuff
from rest_framework.routers import DefaultRouter

# nexus Stuff
from nexus.base.api.routers import SingletonRouter
from nexus.proposals.api import ProposalViewSet
from nexus.social_media.api import (
    CampaignViewSet,
    ContentCalendarViewSet,
    HashtagViewSet,
    PostViewSet,
)
from nexus.users.api import CurrentUserViewSet
from nexus.users.auth.api import AuthViewSet

default_router = DefaultRouter(trailing_slash=False)
singleton_router = SingletonRouter(trailing_slash=False)

# Register all the django rest framework viewsets below.
default_router.register('auth', AuthViewSet, basename='auth')
singleton_router.register('me', CurrentUserViewSet, basename='me')
default_router.register('posts', PostViewSet, basename='posts')
default_router.register('hashtags', HashtagViewSet, basename='hashtags')
default_router.register('calendars', ContentCalendarViewSet, basename='calendars')
default_router.register('campaigns', CampaignViewSet, basename='campaigns')
default_router.register('proposals', ProposalViewSet, basename='proposal')

# Combine urls from both default and singleton routers and expose as
# 'urlpatterns' which django can pick up from this module.
urlpatterns = default_router.urls + singleton_router.urls
