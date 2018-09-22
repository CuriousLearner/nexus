# Third Party Stuff
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action

# nexus Stuff
from nexus.base import response
from nexus.proposals import models, serializers
from nexus.proposals.permissions import IsCoreOrganizer, IsOwner


class ProposalViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.Proposal.objects.all()
    serializer_class = serializers.ProposalSerializer

    @action(methods=['PATCH'], detail=True, permission_classes=(IsCoreOrganizer,))
    def accept(self, request, pk):
        data = {'status': 'accepted', 'approved_at': timezone.now()}
        instance = self.get_object()
        serializer = self.serializer_class(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)

    @action(methods=['PATCH'], detail=True, permission_classes=(IsOwner,))
    def retract(self, request, pk):
        data = {'status': 'retracted'}
        instance = self.get_object()
        serializer = self.serializer_class(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)
