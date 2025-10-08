# Third Party Stuff
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action

# nexus Stuff
from nexus.base import response
from nexus.proposals import filters as proposal_filters, models, notifications, serializers
from nexus.users.auth.permissions import has_perm


class ProposalViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = models.Proposal.objects.order_by('-submitted_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = proposal_filters.ProposalFilter
    search_fields = ['title', 'abstract', 'description', 'speaker__email', 'speaker__first_name', 'speaker__last_name']
    ordering_fields = ['submitted_at', 'accepted_at', 'title']

    def get_serializer_class(self):
        if self.action in ('accept', 'retract'):
            return serializers.ProposalStatusUpdateSerializer
        else:
            return serializers.ProposalSerializer

    def perform_create(self, serializer):
        """Send notification email when proposal is created"""
        proposal = serializer.save()
        notifications.send_proposal_submitted_notification(proposal)

    @action(methods=['POST'], detail=True)
    def accept(self, request, pk):
        proposal = get_object_or_404(models.Proposal, pk=pk)
        has_perm('can_accept_proposal', request.user, proposal, raise_exception=True)
        old_status = proposal.status
        data = {
            'status': models.Proposal.STATUS_CHOICES.ACCEPTED,
            'accepted_at': timezone.now(),
        }
        serializer = self.get_serializer(proposal, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        notifications.send_proposal_status_update_notification(proposal, old_status, proposal.status)
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

    @action(methods=['GET'], detail=False)
    def export_csv(self, request):
        """Export proposals to CSV format"""
        import csv
        from django.http import HttpResponse

        queryset = self.filter_queryset(self.get_queryset())

        response_csv = HttpResponse(content_type='text/csv')
        response_csv['Content-Disposition'] = 'attachment; filename="proposals_export.csv"'

        writer = csv.writer(response_csv)
        writer.writerow(['ID', 'Title', 'Speaker', 'Kind', 'Level', 'Status',
                        'Duration', 'Submitted At', 'Accepted At', 'Abstract', 'Description'])

        for proposal in queryset:
            writer.writerow([
                str(proposal.id),
                proposal.title,
                proposal.speaker.email,
                proposal.kind.kind,
                proposal.get_level_display(),
                proposal.get_status_display(),
                str(proposal.duration),
                proposal.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                proposal.accepted_at.strftime('%Y-%m-%d %H:%M:%S') if proposal.accepted_at else '',
                proposal.abstract or '',
                proposal.description or ''
            ])

        return response_csv
