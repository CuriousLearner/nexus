from django.utils import timezone

# Third Party Stuff
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import mixins

from nexus.proposals import models, serializers
from nexus.proposals.permissions import IsCoreOrganizer, IsOwner


class ProposalViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.Proposal.objects.all()
    serializer_class = serializers.ProposalSerializer

    @action(methods=['PATCH'], detail=True, permission_classes=(IsCoreOrganizer,))
    def approve(self, request, pk=None):
        data = {'status': 'accepted', 'approved_at': timezone.now()}
        self.update_proposal_status(data)

    @action(methods=['PATCH'], detail=True, permission_classes=(IsOwner,))
    def retract(self, request, pk=None):
        data = {'status': 'retracted'}
        self.update_proposal_status(data)

    def update_proposal_status(self, data):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()