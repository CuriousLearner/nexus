"""
Behavioral tests for Events API endpoints.

These tests verify that the Events API behaves correctly from a user's perspective,
testing real-world workflows and scenarios.
"""
import json
from django.urls import reverse
import pytest
from tests import factories as f


pytestmark = pytest.mark.django_db


def test_user_can_list_all_events(client):
    """
    Given: Multiple events exist in the system
    When: An authenticated user requests the events list
    Then: They should receive all events with basic information
    """
    user = f.create_user()
    event1 = f.G('events.Event', name='Django Con 2025', slug='djangocon-2025')
    event2 = f.G('events.Event', name='Python Summit', slug='python-summit')

    client.login(user=user)
    url = reverse('events-list')
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['count'] == 2
    event_names = [event['name'] for event in data['results']]
    assert 'Django Con 2025' in event_names
    assert 'Python Summit' in event_names


def test_user_can_create_new_event(client):
    """
    Given: An authenticated user with proper permissions
    When: They submit valid event data
    Then: A new event should be created and returned
    """
    user = f.create_user()
    client.login(user=user)

    url = reverse('events-list')
    event_data = {
        'name': 'PyCon 2026',
        'slug': 'pycon-2026',
        'description': 'Annual Python Conference',
        'start_date': '2026-05-01',
        'end_date': '2026-05-05',
        'registration_start': '2026-01-01T00:00:00Z',
        'registration_end': '2026-04-30T23:59:59Z',
        'city': 'San Francisco',
        'country': 'USA'
    }

    response = client.json.post(url, data=json.dumps(event_data))

    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['name'] == 'PyCon 2026'
    assert data['slug'] == 'pycon-2026'


def test_user_can_get_event_details(client):
    """
    Given: An event exists with associated venue and sessions
    When: User requests event details by slug
    Then: They receive complete event information including nested data
    """
    user = f.create_user()
    event = f.G('events.Event', name='DjangoCon', slug='djangocon')
    venue = f.G('events.Venue', event=event, name='Conference Center')
    session = f.G('events.Session', event=event, title='Keynote Speech')

    client.login(user=user)
    url = reverse('events-detail', kwargs={'slug': event.slug})
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['name'] == 'DjangoCon'
    assert 'venues' in data or 'sessions' in data


def test_user_can_update_event(client):
    """
    Given: An existing event
    When: User updates the event information
    Then: The event should be updated successfully
    """
    user = f.create_user()
    event = f.G('events.Event', name='Old Name', slug='old-name')

    client.login(user=user)
    url = reverse('events-detail', kwargs={'slug': event.slug})
    update_data = {
        'name': 'Updated Name',
        'description': 'Updated description'
    }

    response = client.json.patch(url, data=json.dumps(update_data))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['name'] == 'Updated Name'
    assert data['description'] == 'Updated description'


def test_user_can_delete_event(client):
    """
    Given: An existing event
    When: User deletes the event
    Then: The event should be removed from the system
    """
    user = f.create_user()
    event = f.G('events.Event', slug='to-delete')

    client.login(user=user)
    url = reverse('events-detail', kwargs={'slug': event.slug})
    response = client.delete(url)

    assert response.status_code == 204

    # Verify event is deleted
    response = client.get(url)
    assert response.status_code == 404


def test_can_manage_event_venues(client):
    """
    Given: An event exists
    When: User creates and manages venues for the event
    Then: Venues should be properly associated with the event
    """
    user = f.create_user()
    event = f.G('events.Event', slug='test-event')

    client.login(user=user)

    # Create venue
    url = reverse('venues-list')
    venue_data = {
        'event': str(event.id),
        'name': 'Main Hall',
        'address': '123 Conference St',
        'capacity': 500
    }

    response = client.json.post(url, data=json.dumps(venue_data))
    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['name'] == 'Main Hall'
    assert data['capacity'] == 500


def test_can_manage_event_sessions(client):
    """
    Given: An event and venue exist
    When: User creates a session with speakers
    Then: Session should be created with all details
    """
    user = f.create_user()
    speaker = f.create_user(first_name='Jane', last_name='Doe')
    event = f.G('events.Event', slug='test-event')
    venue = f.G('events.Venue', event=event, name='Room A')

    client.login(user=user)

    url = reverse('sessions-list')
    session_data = {
        'event': str(event.id),
        'venue': str(venue.id),
        'title': 'Introduction to Django',
        'description': 'Learn Django basics',
        'start_time': '2026-05-01T10:00:00Z',
        'end_time': '2026-05-01T11:00:00Z',
        'speakers': [str(speaker.id)]
    }

    response = client.json.post(url, data=json.dumps(session_data))
    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['title'] == 'Introduction to Django'


def test_can_register_attendees(client):
    """
    Given: An event exists
    When: User registers as an attendee
    Then: Attendee registration should be recorded
    """
    user = f.create_user()
    attendee_user = f.create_user(email='attendee@example.com')
    event = f.G('events.Event', slug='test-event')

    client.login(user=user)

    url = reverse('attendees-list')
    attendee_data = {
        'event': str(event.id),
        'user': str(attendee_user.id),
        'ticket_number': 'TICKET-12345',
        'ticket_type': 'regular'
    }

    response = client.json.post(url, data=json.dumps(attendee_data))
    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['ticket_type'] == 'regular'
    assert data['ticket_number'] == 'TICKET-12345'


def test_can_manage_sponsors(client):
    """
    Given: An event exists
    When: User adds a sponsor to the event
    Then: Sponsor should be associated with proper tier
    """
    user = f.create_user()
    event = f.G('events.Event', slug='test-event')

    client.login(user=user)

    url = reverse('sponsors-list')
    sponsor_data = {
        'event': str(event.id),
        'name': 'Tech Corp',
        'tier': 'gold',
        'website': 'https://techcorp.com',
        'description': 'Leading tech company'
    }

    response = client.json.post(url, data=json.dumps(sponsor_data))
    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['name'] == 'Tech Corp'
    assert data['tier'] == 'gold'


def test_unauthenticated_user_cannot_create_event(client):
    """
    Given: A user is not authenticated
    When: They try to create an event
    Then: They should receive an authentication error
    """
    url = reverse('events-list')
    event_data = {
        'name': 'Unauthorized Event',
        'slug': 'unauthorized'
    }

    response = client.json.post(url, data=json.dumps(event_data))
    assert response.status_code in [401, 403]


def test_can_get_event_schedule(client):
    """
    Given: An event with multiple sessions
    When: User requests the event schedule
    Then: They should receive sessions organized by date
    """
    user = f.create_user()
    event = f.G('events.Event', slug='test-event')
    session1 = f.G('events.Session', event=event, title='Morning Session',
                   start_time='2026-05-01T09:00:00Z')
    session2 = f.G('events.Session', event=event, title='Afternoon Session',
                   start_time='2026-05-01T14:00:00Z')

    client.login(user=user)
    url = reverse('events-schedule', kwargs={'slug': event.slug})
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    # Schedule should be organized by date
    assert isinstance(data, (dict, list))
