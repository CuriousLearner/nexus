# Third Party Stuff
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

# nexus Stuff
from nexus.base import response

from . import filters as user_filters, models, serializers


class CurrentUserViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = user_filters.UserFilter
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'email', 'first_name', 'last_name']

    def get_object(self):
        return self.request.user

    def list(self, request):
        """Get logged in user profile"""
        serializer = self.get_serializer(self.get_object())
        return response.Ok(serializer.data)

    def partial_update(self, request):
        """Update logged in user profile"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)
