# Third Party Stuff
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action

# nexus Stuff
from nexus.base import response
from nexus.proposals import models, serializers
from nexus.users.auth.permissions import has_perm


class ProposalViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = models.Proposal.objects.all()
    serializer_class = serializers.ProposalSerializer

    @action(methods=['PATCH'], detail=True)
    def accept(self, request, pk):
        data = {'status': 'accepted', 'approved_at': timezone.now()}
        proposal = get_object_or_404(models.Proposal, pk=pk)
        has_perm('can_accept_proposal', request.user, proposal, raise_exception=True)
        serializer = self.get_serializer(proposal, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)

    @action(methods=['PATCH'], detail=True)
    def retract(self, request, pk):
        data = {'status': 'retracted'}
        proposal = get_object_or_404(models.Proposal, pk=pk)
        has_perm('can_retract_proposal', request.user, proposal, raise_exception=True)
        serializer = self.get_serializer(proposal, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)
