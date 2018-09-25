# Third Party Stuff
import pytest
from django.apps import apps
from django.urls import reverse
from tests import factories as f
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_proposal_creation_api(client):
    Proposal = apps.get_model('proposals.Proposal')
    url = reverse('proposal-list')
    user = f.create_user()
    data = {
        'title': 'Test Proposal',
        'kind': 'talk',
        'level': 'beginner',
        'duration': '00:30:00',
        'abstract': 'Proposal abstract',
        'description': 'Proposal description',
    }
    client.login(user)

    response = client.post(url, data=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["speaker"] == user.email
    assert response.data["submitted_at"] is not None
    assert response.data["modified_at"] is not None
    assert response.data["status"] == Proposal.STATUS_CHOICES.SUBMITTED


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


def test_proposal_listing_api(client):

    no_of_test_proposals = 3
    data = {
        'page': 2,
        'per_page': 1,
    }
    for x in range(no_of_test_proposals):
        f.create_proposal()
    url = reverse('proposal-list')
    user = f.create_user()

    client.login(user)
    response = client.get(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    expected_keys = (
        'count', 'next', 'previous', 'results'
    )
    assert set(response.data.keys()) == set(expected_keys)
    assert response.data['previous'] is not None
    assert response.data['next'] is not None
    assert response.data['count'] == no_of_test_proposals
    assert response.data['results'] is not None
