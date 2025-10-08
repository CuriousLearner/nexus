# Third Party Stuff
import django_filters

# Nexus Stuff
from nexus.proposals.models import Proposal


class ProposalFilter(django_filters.FilterSet):
    """Filter for Proposal model to enable searching and filtering"""

    title = django_filters.CharFilter(lookup_expr='icontains')
    speaker = django_filters.CharFilter(field_name='speaker__email', lookup_expr='icontains')
    level = django_filters.ChoiceFilter(choices=Proposal.LEVELS_CHOICES)
    status = django_filters.ChoiceFilter(choices=Proposal.STATUS_CHOICES)
    kind = django_filters.CharFilter(field_name='kind__kind', lookup_expr='icontains')
    abstract = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Proposal
        fields = ['level', 'status', 'kind']
