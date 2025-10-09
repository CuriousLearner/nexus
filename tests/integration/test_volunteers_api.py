"""
Behavioral tests for Volunteers API endpoints.

These tests verify volunteer management workflows including role assignment,
shift scheduling, task management, and hours tracking.
"""
import json
from django.urls import reverse
import pytest
from tests import factories as f


pytestmark = pytest.mark.django_db


def test_user_can_list_volunteer_roles(client):
    """
    Given: Multiple volunteer roles exist
    When: An authenticated user requests the roles list
    Then: They should receive all available roles
    """
    user = f.create_user()
    role1 = f.G('volunteers.VolunteerRole', name='Registration Desk', is_active=True)
    role2 = f.G('volunteers.VolunteerRole', name='Tech Support', is_active=True)

    client.login(user=user)
    url = reverse('volunteer-roles-list')
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['count'] == 2
    role_names = [role['name'] for role in data['results']]
    assert 'Registration Desk' in role_names
    assert 'Tech Support' in role_names


def test_can_create_volunteer_role(client):
    """
    Given: An authenticated user
    When: They create a new volunteer role
    Then: The role should be created with all details
    """
    user = f.create_user()
    client.login(user=user)

    url = reverse('volunteer-roles-list')
    role_data = {
        'name': 'Speaker Liaison',
        'description': 'Assist speakers with their needs',
        'required_skills': 'Good communication, organization',
        'volunteers_needed': 5,
        'is_active': True
    }

    response = client.json.post(url, data=json.dumps(role_data))

    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['name'] == 'Speaker Liaison'
    assert data['volunteers_needed'] == 5


def test_can_create_volunteer_shift(client):
    """
    Given: A volunteer role and event exist
    When: User creates a shift for the role
    Then: Shift should be created with time and location
    """
    user = f.create_user()
    event = f.G('events.Event', name='Conference 2026')
    role = f.G('volunteers.VolunteerRole', name='Security')

    client.login(user=user)

    url = reverse('volunteer-shifts-list')
    shift_data = {
        'event': str(event.id),
        'role': str(role.id),
        'title': 'Morning Security Shift',
        'description': 'Guard main entrance',
        'start_time': '2026-05-01T08:00:00Z',
        'end_time': '2026-05-01T12:00:00Z',
        'max_volunteers': 3,
        'location': 'Main Entrance',
        'status': 'open'
    }

    response = client.json.post(url, data=json.dumps(shift_data))

    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['title'] == 'Morning Security Shift'
    assert data['max_volunteers'] == 3


def test_can_assign_volunteer_to_shift(client):
    """
    Given: A shift exists with available slots
    When: User assigns a volunteer to the shift
    Then: Volunteer should be assigned with pending status
    """
    user = f.create_user()
    volunteer = f.create_user(first_name='John', last_name='Volunteer')
    event = f.G('events.Event')
    role = f.G('volunteers.VolunteerRole')
    shift = f.G('volunteers.VolunteerShift', event=event, role=role, max_volunteers=5)

    client.login(user=user)

    # Use the custom action endpoint
    url = reverse('volunteer-shifts-assign-volunteer', kwargs={'pk': shift.id})
    assignment_data = {
        'volunteer_id': str(volunteer.id)
    }

    response = client.json.post(url, data=json.dumps(assignment_data))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert 'volunteer' in data or 'volunteer_email' in data


def test_cannot_assign_volunteer_to_full_shift(client):
    """
    Given: A shift that is already full
    When: User tries to assign another volunteer
    Then: They should receive an error
    """
    user = f.create_user()
    volunteer = f.create_user()
    event = f.G('events.Event')
    role = f.G('volunteers.VolunteerRole')
    shift = f.G('volunteers.VolunteerShift', event=event, role=role, max_volunteers=1)

    # Fill the shift
    f.G('volunteers.VolunteerAssignment', shift=shift, volunteer=user, status='confirmed')

    client.login(user=user)

    url = reverse('volunteer-shifts-assign-volunteer', kwargs={'pk': shift.id})
    assignment_data = {
        'volunteer_id': str(volunteer.id)
    }

    response = client.json.post(url, data=json.dumps(assignment_data))

    assert response.status_code == 400


def test_can_confirm_volunteer_assignment(client):
    """
    Given: A pending volunteer assignment
    When: User confirms the assignment
    Then: Assignment status should change to confirmed
    """
    user = f.create_user()
    volunteer = f.create_user()
    shift = f.G('volunteers.VolunteerShift')
    assignment = f.G('volunteers.VolunteerAssignment',
                     shift=shift, volunteer=volunteer, status='pending')

    client.login(user=user)

    url = reverse('volunteer-assignments-confirm', kwargs={'pk': assignment.id})
    response = client.json.post(url, data=json.dumps({}))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 'confirmed'


def test_can_check_in_volunteer(client):
    """
    Given: A confirmed volunteer assignment
    When: Volunteer checks in for their shift
    Then: Check-in time should be recorded
    """
    user = f.create_user()
    volunteer = f.create_user()
    shift = f.G('volunteers.VolunteerShift')
    assignment = f.G('volunteers.VolunteerAssignment',
                     shift=shift, volunteer=volunteer, status='confirmed')

    client.login(user=user)

    url = reverse('volunteer-assignments-check-in', kwargs={'pk': assignment.id})
    response = client.json.post(url, data=json.dumps({}))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 'checked_in'
    assert data['checked_in_at'] is not None


def test_can_complete_volunteer_assignment(client):
    """
    Given: A volunteer who has checked in
    When: Their shift is completed
    Then: Completion time and hours should be recorded
    """
    user = f.create_user()
    volunteer = f.create_user()
    shift = f.G('volunteers.VolunteerShift')
    assignment = f.G('volunteers.VolunteerAssignment',
                     shift=shift, volunteer=volunteer, status='checked_in')

    client.login(user=user)

    url = reverse('volunteer-assignments-complete', kwargs={'pk': assignment.id})
    response = client.json.post(url, data=json.dumps({}))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 'completed'
    assert data['completed_at'] is not None


def test_can_create_volunteer_task(client):
    """
    Given: An event and volunteer exist
    When: User creates a task and assigns it
    Then: Task should be created with assignment
    """
    user = f.create_user()
    volunteer = f.create_user()
    event = f.G('events.Event')

    client.login(user=user)

    url = reverse('volunteer-tasks-list')
    task_data = {
        'event': str(event.id),
        'title': 'Set up registration desk',
        'description': 'Arrange tables and materials',
        'assigned_to': str(volunteer.id),
        'status': 'todo',
        'priority': 'high',
        'due_date': '2026-05-01T08:00:00Z'
    }

    response = client.json.post(url, data=json.dumps(task_data))

    assert response.status_code == 201
    data = json.loads(response.content)
    assert data['title'] == 'Set up registration desk'
    assert data['priority'] == 'high'


def test_can_complete_volunteer_task(client):
    """
    Given: An assigned task
    When: Volunteer completes the task
    Then: Task status should update to completed
    """
    user = f.create_user()
    volunteer = f.create_user()
    event = f.G('events.Event')
    task = f.G('volunteers.VolunteerTask',
               event=event, assigned_to=volunteer, assigned_by=user, status='todo')

    client.login(user=user)

    url = reverse('volunteer-tasks-complete', kwargs={'pk': task.id})
    response = client.json.post(url, data=json.dumps({}))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 'completed'


def test_can_track_volunteer_hours(client):
    """
    Given: A volunteer has completed shifts
    When: User requests volunteer hours
    Then: Total hours should be calculated
    """
    user = f.create_user()
    volunteer = f.create_user()
    event = f.G('events.Event')

    # Create hours record
    hours = f.G('volunteers.VolunteerHours',
                volunteer=volunteer, event=event, total_hours=8.5)

    client.login(user=user)

    url = reverse('volunteer-hours-detail', kwargs={'pk': hours.id})
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    # DecimalField serialized as string
    assert float(data['total_hours']) == 8.5


def test_can_get_volunteer_leaderboard(client):
    """
    Given: Multiple volunteers with different hours
    When: User requests the leaderboard
    Then: Volunteers should be ranked by hours
    """
    user = f.create_user()
    event = f.G('events.Event')

    volunteer1 = f.create_user(first_name='Alice')
    volunteer2 = f.create_user(first_name='Bob')

    f.G('volunteers.VolunteerHours', volunteer=volunteer1, event=event, total_hours=10)
    f.G('volunteers.VolunteerHours', volunteer=volunteer2, event=event, total_hours=5)

    client.login(user=user)

    url = reverse('volunteer-hours-leaderboard')
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) >= 2
    # First volunteer should have more hours (leaderboard returns sorted list, not paginated)
    assert float(data[0]['total_hours']) >= float(data[1]['total_hours'])


def test_can_get_available_shifts(client):
    """
    Given: Mix of full and available shifts
    When: User requests available shifts
    Then: Only non-full shifts should be returned
    """
    user = f.create_user()
    event = f.G('events.Event')
    role = f.G('volunteers.VolunteerRole')

    # Available shift
    available_shift = f.G('volunteers.VolunteerShift',
                         event=event, role=role, max_volunteers=5)

    # Full shift
    full_shift = f.G('volunteers.VolunteerShift',
                     event=event, role=role, max_volunteers=1)
    f.G('volunteers.VolunteerAssignment', shift=full_shift, volunteer=user)

    client.login(user=user)

    url = reverse('volunteer-shifts-available')
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    # Available endpoint returns list, not paginated results
    shift_ids = [shift['id'] for shift in data]
    assert str(available_shift.id) in shift_ids


def test_unauthenticated_user_cannot_access_volunteers(client):
    """
    Given: A user is not authenticated
    When: They try to access volunteer endpoints
    Then: They should receive an authentication error
    """
    url = reverse('volunteer-roles-list')
    response = client.get(url)
    assert response.status_code in [401, 403]
