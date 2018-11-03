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
                      viewsets.GenericViewSet):
    queryset = models.Proposal.objects.order_by('-submitted_at')

    def get_serializer_class(self):
        if self.action in ('accept', 'retract'):
            return serializers.ProposalStatusUpdateSerializer
        else:
            return serializers.ProposalSerializer

    @action(methods=['POST'], detail=True)
    def accept(self, request, pk):
        proposal = get_object_or_404(models.Proposal, pk=pk)
        has_perm('can_accept_proposal', request.user, proposal, raise_exception=True)
        data = {
            'status': models.Proposal.STATUS_CHOICES.ACCEPTED,
            'accepted_at': timezone.now(),
        }
        serializer = self.get_serializer(proposal, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=True)
    def retract(self, request, pk):
        proposal = get_object_or_404(models.Proposal, pk=pk)
        has_perm('can_retract_proposal', request.user, proposal, raise_exception=True)
        data = {
            'status': models.Proposal.STATUS_CHOICES.RETRACTED,
        }
        serializer = self.get_serializer(proposal, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)
