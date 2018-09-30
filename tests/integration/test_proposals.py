# Third Party Stuff
import pytest
from django.apps import apps
from django.urls import reverse
from rest_framework import status
from tests import factories as f

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

    f.create_proposal_kind(kind='talk')
    response = client.post(url, data=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["speaker"] == user.email
    assert response.data["submitted_at"] is not None
    assert response.data["modified_at"] is not None
    assert response.data["status"] == Proposal.STATUS_CHOICES.SUBMITTED

    proposal = Proposal.objects.get(id=response.data["id"])
    assert proposal.title == response.data["title"]


def test_proposal_acceptance_api(client):
    Proposal = apps.get_model('proposals.Proposal')
    proposal = f.create_proposal(status=Proposal.STATUS_CHOICES.SUBMITTED, accepted_at=None)
    url = reverse('proposal-accept', kwargs={'pk': proposal.id})
    response = client.post(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    user = f.create_user(is_core_organizer=False)

    # Check that user who is not core-organizer
    # is unable to accept proposal
    client.login(user)
    response = client.post(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Make user a core-organizer to accept this proposal
    user.is_core_organizer = True
    user.save()
    user.refresh_from_db()

    # Check that `accepted_at` time is still `None`
    assert proposal.accepted_at is None

    client.login(user)
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    proposal.refresh_from_db()
    expected_keys = (
        'id', 'title', 'speaker', 'status', 'kind', 'level', 'duration',
        'abstract', 'description', 'submitted_at', 'accepted_at',
        'modified_at'
    )
    assert set(response.data.keys()).issubset(expected_keys)
    # Check that status is accepted and `accepted_at` now has a value.
    assert proposal.status == Proposal.STATUS_CHOICES.ACCEPTED
    assert proposal.accepted_at is not None


def test_proposal_retraction_api(client):
    Proposal = apps.get_model('proposals.Proposal')
    proposal = f.create_proposal(status=Proposal.STATUS_CHOICES.SUBMITTED)
    url = reverse('proposal-retract', kwargs={'pk': proposal.id})
    response = client.post(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    user = f.create_user(is_core_organizer=False)

    # Check that normal user cannot take this action
    client.login(user)
    response = client.post(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    user.is_core_organizer = True
    user.save()
    user.refresh_from_db()

    # Check that core-organizer can take this action.
    client.login(user)
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    proposal.refresh_from_db()
    expected_keys = (
        'id', 'title', 'speaker', 'status', 'kind', 'level', 'duration',
        'abstract', 'description', 'submitted_at', 'accepted_at',
        'modified_at'
    )
    assert set(response.data.keys()).issubset(expected_keys)
    assert proposal.status == Proposal.STATUS_CHOICES.RETRACTED


def test_proposal_listing_api(client):

    no_of_test_proposals = 6
    data = {
        'page': 2,
        'per_page': 2,
    }
    f.create_proposal(n=no_of_test_proposals)
    url = reverse('proposal-list')
    user = f.create_user()

    client.login(user)
    response = client.get(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['previous'] is not None
    assert response.data['next'] is not None
    assert response.data['count'] == no_of_test_proposals
    assert response.data['results'] is not None
    assert response.data['results'][0]['submitted_at'] > response.data['results'][1]['submitted_at']
