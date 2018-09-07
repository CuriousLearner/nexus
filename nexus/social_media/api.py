from django.utils import timezone

# Third Party Stuff
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from nexus.base import response
from . import models, serializers, permissions


class PostViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                  mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.Post.objects.all()
    permission_classes = (IsAuthenticated, permissions.IsAdminOrAuthorOfPost)

    def get_serializer_class(self):
        if self.action in ['approve', 'posted']:
            return serializers.AdminPostSerializer
        return serializers.PostSerializer

    @action(methods=['PATCH'], detail=True, permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        instance = self.get_object()
        data = {'is_approved': True, 'approval_time': timezone.now()}
        return self.update_post_status(instance, data)

    @action(methods=['PATCH'], detail=True, permission_classes=[IsAdminUser])
    def posted(self, request, pk=None):
        instance = self.get_object()
        data = {'is_posted': True, 'posted_time': timezone.now()}
        return self.update_post_status(instance, data)

    @action(methods=['POST', 'PUT', 'DELETE'], detail=True)
    @parser_classes((FormParser, MultiPartParser))
    def image(self, request, pk=None):
        instance = self.get_object()
        if request.method == 'DELETE':
            if instance.image == '':
                return response.BadRequest({'error_message': 'Image is not present'})
            instance.image.delete(save=True)
            return self.update_post_status(instance)
        if request.FILES:
            if request.method == 'POST':
                if not instance.image == '':
                    return response.BadRequest({'error_message': 'Image already present'})
                data = {'image': request.data['image']}
                return self.update_post_status(instance, data)
            elif request.method == 'PUT':
                data = {'image': request.data['image']}
                return self.update_post_status(instance, data)
        return response.BadRequest({'error_message': 'Image file missing from the request'})

    def update_post_status(self, instance, data={}):
        serializer_class = self.get_serializer_class()
        if not instance.is_posted:
            serializer = serializer_class(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = serializer_class(instance)
        return response.Ok(serializer.data)
