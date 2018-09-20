# Third party stuff
from django.test import TestCase

# nexus stuff
from tests import factories as f
from nexus.proposals.models import Proposal


class TestProposalModel(TestCase):

    def setUp(self):
        self.user = f.create_user(email='f@F.com', password='abc')

    def test_create_proposal(self):
        proposal = {
            'title': 'Model testing',
            'kind': 't',
            'level': 'b',
            'duration': '01:00:00',
            'abstract': 'Abstract of proposal',
            'description': 'Description of proposal',
            'speaker': self.user
        }
        proposal = Proposal.objects.create(**proposal)
        assert proposal.id
        assert proposal.title == 'Model testing'
        assert str(proposal.speaker) == str(self.user)
        assert proposal.status == 's'
        assert proposal.kind == 't'
        assert proposal.level == 'b'
        assert proposal.duration == '01:00:00'
        assert proposal.abstract == 'Abstract of proposal'
        assert proposal.description == 'Description of proposal'
        assert proposal.submitted_at
        assert proposal.approved_at is None
        assert proposal.modified_at

