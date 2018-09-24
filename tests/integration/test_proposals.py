# Third Party Stuff
import pytest
from django.apps import apps
from django.urls import reverse
from tests import factories as f
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_proposal_acceptance_api(client):
    Proposal = apps.get_model('proposals.Proposal')
    proposal = f.create_proposal(status=Proposal.STATUS_CHOICES.SUBMITTED)
    url = reverse('proposal-accept', kwargs={'pk': proposal.id})
    response = client.patch(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    user = f.create_user(is_core_organizer=False)

    client.login(user)
    response = client.patch(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    user.is_core_organizer = True
    user.save()
    user.refresh_from_db()

    client.login(user)
    response = client.patch(url)
    assert response.status_code == status.HTTP_200_OK
    proposal.refresh_from_db()
    expected_keys = (
        'id', 'title', 'speaker', 'status', 'kind', 'level', 'duration',
        'abstract', 'description', 'submitted_at', 'approved_at',
        'modified_at'
    )
    assert set(response.data.keys()).issubset(expected_keys)
    assert proposal.status == Proposal.STATUS_CHOICES.ACCEPTED
    assert proposal.approved_at is not None


def test_proposal_retraction_api(client):
    Proposal = apps.get_model('proposals.Proposal')
    proposal = f.create_proposal(status=Proposal.STATUS_CHOICES.SUBMITTED)
    url = reverse('proposal-retract', kwargs={'pk': proposal.id})
    response = client.patch(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    user = f.create_user(is_core_organizer=False)

    client.login(user)
    response = client.patch(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    user.is_core_organizer = True
    user.save()
    user.refresh_from_db()

    client.login(user)
    response = client.patch(url)
    assert response.status_code == status.HTTP_200_OK
    proposal.refresh_from_db()
    expected_keys = (
        'id', 'title', 'speaker', 'status', 'kind', 'level', 'duration',
        'abstract', 'description', 'submitted_at', 'approved_at',
        'modified_at'
    )
    assert set(response.data.keys()).issubset(expected_keys)
    assert proposal.status == Proposal.STATUS_CHOICES.RETRACTED
