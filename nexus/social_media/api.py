# Third Party Stuff
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

# nexus Stuff
from nexus.base import response
from nexus.social_media import models, permissions, serializers
from nexus.social_media.tasks import task_to_post_to_twitter


class PostViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                  mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.Post.objects.all().order_by('-scheduled_time')
    permission_classes = (IsAuthenticated, permissions.IsAdminOrAuthorOfPost)

    def get_serializer_class(self):
        if self.action in ('approve', 'publish'):
            return serializers.AdminPostSerializer
        return serializers.PostSerializer

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsCoreOrganizer])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_approved:
            data = {'is_approved': True, 'approval_time': timezone.now()}
            serializer = self.get_serializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if instance.posted_at == 'twitter':
                task_to_post_to_twitter.delay(instance.id)
            return response.Ok(serializer.data)
        else:
            serializer = self.get_serializer(instance)
            return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsCoreOrganizer])
    def publish(self, request, pk=None):
        instance = self.get_object()
        if not instance.is_approved:
            return response.BadRequest({'error_message': 'Post has not been approved yet'})
        if not instance.is_posted:
            data = {'is_posted': True, 'posted_time': timezone.now()}
            serializer = self.get_serializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Ok(serializer.data)
        else:
            serializer = self.get_serializer(instance)
            return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    @parser_classes((FormParser, MultiPartParser))
    def upload_image(self, request, pk=None):
        instance = self.get_object()
        if request.FILES:
            data = request.data
            serializer = self.get_serializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Ok(serializer.data)
        return response.BadRequest({'error_message': 'Image file missing from the request'})

    @action(methods=['POST'], detail=True)
    @parser_classes((FormParser, MultiPartParser))
    def delete_image(self, request, pk=None):
        instance = self.get_object()
        if not instance.image:
            return response.BadRequest({'error_message': 'Image is not present for this post'})
        instance.image.delete(save=True)
        serializer = self.get_serializer(instance)
        return response.Ok(serializer.data)
