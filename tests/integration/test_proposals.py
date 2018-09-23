# Third Party Stuff
import pytest
from django.apps import apps
from django.urls import reverse
from tests import factories as f

pytestmark = pytest.mark.django_db


def test_proposal_acceptance_api(client):
    Proposal = apps.get_model('proposals.Proposal')
    proposal = f.create_proposal(status=Proposal.STATUS_CHOICES.SUBMITTED)
    url = reverse('proposal-accept', kwargs={'pk': proposal.id})
    response = client.patch(url)
    assert response.status_code == 401

    user = f.create_user(is_core_organizer=False)

    client.login(user)
    response = client.patch(url)
    assert response.status_code == 403

    user.is_core_organizer = True
    user.save()
    user.refresh_from_db()

    client.login(user)
    response = client.patch(url)
    assert response.status_code == 200
    expected_keys = (
        'id', 'title', 'speaker', 'status', 'kind', 'level', 'duration',
        'abstract', 'description', 'submitted_at', 'approved_at',
        'modified_at'
    )
    assert set(response.data.keys()).issubset(expected_keys)
    assert proposal.status == Proposal.STATUS_CHOICES.ACCEPTED
