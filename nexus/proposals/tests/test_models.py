# Third Party Stuff
from django.test import TestCase
from tests import factories as f

# nexus Stuff
from nexus.proposals.models import Proposal, ProposalKind


class ProposalModelTestCase(TestCase):

    def setUp(self):
        self.user = f.create_user(email='test@example.com', password='test')
        self.proposal_kind = f.create_proposal_kind(kind='talk')

    def test_create_proposal(self):
        proposal = {
            'speaker': self.user,
            'title': 'Test Proposal',
            'kind': self.proposal_kind,
            'level': 'beginner',
            'duration': '00:30:00',
            'abstract': 'Proposal abstract',
            'description': 'Proposal description',
        }
        proposal = Proposal.objects.create(**proposal)
        assert proposal.id
        assert proposal.speaker == self.user
        assert proposal.title == 'Test Proposal'
        assert proposal.kind == self.proposal_kind
        assert proposal.level == Proposal.LEVELS_CHOICES.BEGINNER
        assert proposal.duration == '00:30:00'
        assert proposal.abstract == 'Proposal abstract'
        assert proposal.description == 'Proposal description'
        assert proposal.accepted_at is None
        assert proposal.status == Proposal.STATUS_CHOICES.SUBMITTED
        assert proposal.submitted_at is not None
        assert str(proposal) == str(proposal.title)


class ProposalKindModelTestCase(TestCase):
    def test_create_proposal_kind(self):
        proposal_kind = ProposalKind.objects.create(kind='talk')
        assert str(proposal_kind) == str(proposal_kind.kind)
