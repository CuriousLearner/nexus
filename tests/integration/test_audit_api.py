"""
Behavioral tests for Audit Log API endpoints.

These tests verify audit trail functionality including log retrieval,
filtering, and statistics generation.
"""
import json
from django.urls import reverse
import pytest
from tests import factories as f


pytestmark = pytest.mark.django_db


def test_user_can_list_audit_logs(client):
    """
    Given: Audit logs exist in the system
    When: An authenticated user requests the audit logs
    Then: They should receive the logs with user and action information
    """
    user = f.create_user()
    # Audit logs are typically created automatically by the system
    # We'll create them directly for testing
    f.G('base.AuditLog', user=user, action='create', description='Test Post')
    f.G('base.AuditLog', user=user, action='update', description='Test Event')

    client.login(user=user)
    url = reverse('audit-logs-list')
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['count'] >= 2


def test_can_get_recent_audit_logs(client):
    """
    Given: Multiple audit logs exist
    When: User requests recent logs with a limit
    Then: They should receive the most recent logs
    """
    user = f.create_user()

    # Create several logs
    for i in range(10):
        f.G('base.AuditLog', user=user, action='create', description=f'Object {i}')

    client.login(user=user)
    url = reverse('audit-logs-recent')
    response = client.get(f'{url}?limit=5')

    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) <= 5


def test_can_filter_audit_logs_by_user(client):
    """
    Given: Audit logs from multiple users
    When: User requests logs for a specific user
    Then: Only that user's logs should be returned
    """
    user1 = f.create_user(email='user1@example.com')
    user2 = f.create_user(email='user2@example.com')

    f.G('base.AuditLog', user=user1, action='create')
    f.G('base.AuditLog', user=user1, action='update')
    f.G('base.AuditLog', user=user2, action='delete')

    client.login(user=user1)
    url = reverse('audit-logs-by-user')
    response = client.get(f'{url}?user_id={user1.id}')

    assert response.status_code == 200
    data = json.loads(response.content)
    # Custom action returns list, not paginated results
    assert all(log['user'] == str(user1.id) for log in data)


def test_can_filter_audit_logs_by_object(client):
    """
    Given: Audit logs for different objects
    When: User requests logs for a specific object
    Then: Only that object's logs should be returned
    """
    user = f.create_user()
    from django.contrib.contenttypes.models import ContentType

    # Get content type for User model
    content_type = ContentType.objects.get_for_model(user)

    f.G('base.AuditLog', user=user, content_type=content_type,
        object_id=str(user.id), action='update')

    client.login(user=user)
    url = reverse('audit-logs-by-object')
    response = client.get(f'{url}?content_type_id={content_type.id}&object_id={user.id}')

    assert response.status_code == 200
    data = json.loads(response.content)
    # Custom action returns list, not paginated results
    assert len(data) >= 1


def test_can_get_audit_log_statistics(client):
    """
    Given: Various audit logs with different actions
    When: User requests audit statistics
    Then: They should receive aggregated statistics
    """
    user1 = f.create_user()
    user2 = f.create_user()

    # Create logs with different actions
    f.G('base.AuditLog', user=user1, action='create')
    f.G('base.AuditLog', user=user1, action='create')
    f.G('base.AuditLog', user=user2, action='update')
    f.G('base.AuditLog', user=user2, action='delete')

    client.login(user=user1)
    url = reverse('audit-logs-statistics')
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)

    # Should contain statistics
    assert 'total_logs' in data
    assert 'by_action' in data
    assert 'top_users' in data
    assert data['total_logs'] >= 4


def test_audit_log_includes_user_information(client):
    """
    Given: An audit log exists
    When: User retrieves the log details
    Then: It should include user email and name
    """
    user = f.create_user(first_name='John', last_name='Doe', email='john@example.com')
    log = f.G('base.AuditLog', user=user, action='create', description='Test Object')

    client.login(user=user)
    url = reverse('audit-logs-detail', kwargs={'pk': log.id})
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['user_email'] == 'john@example.com'
    assert 'user_name' in data


def test_audit_log_tracks_changes(client):
    """
    Given: An audit log with change tracking
    When: User retrieves the log
    Then: It should show what fields were changed
    """
    user = f.create_user()
    changes = {'name': ['Old Name', 'New Name'], 'status': ['active', 'inactive']}
    log = f.G('base.AuditLog', user=user, action='update',
              description='Test', changes=changes)

    client.login(user=user)
    url = reverse('audit-logs-detail', kwargs={'pk': log.id})
    response = client.get(url)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['changes'] == changes


def test_can_search_audit_logs(client):
    """
    Given: Audit logs with different descriptions
    When: User searches by text
    Then: Matching logs should be returned
    """
    user = f.create_user()
    f.G('base.AuditLog', user=user, description='Important Event')
    f.G('base.AuditLog', user=user, description='Regular Post')

    client.login(user=user)
    url = reverse('audit-logs-list')
    response = client.get(f'{url}?search=Important')

    assert response.status_code == 200
    data = json.loads(response.content)
    # Should find the log with "Important" in it
    assert any('Important' in log.get('description', '') for log in data['results'])


def test_can_filter_by_action_type(client):
    """
    Given: Logs with different action types
    When: User filters by specific action
    Then: Only logs with that action should be returned
    """
    user = f.create_user()
    f.G('base.AuditLog', user=user, action='create')
    f.G('base.AuditLog', user=user, action='create')
    f.G('base.AuditLog', user=user, action='delete')

    client.login(user=user)
    url = reverse('audit-logs-list')
    response = client.get(f'{url}?action=create')

    assert response.status_code == 200
    data = json.loads(response.content)
    assert all(log['action'] == 'create' for log in data['results'])


def test_audit_logs_are_read_only(client):
    """
    Given: An audit log exists
    When: User tries to modify or delete it
    Then: The operation should not be allowed
    """
    user = f.create_user()
    log = f.G('base.AuditLog', user=user, action='create')

    client.login(user=user)

    # Try to update
    url = reverse('audit-logs-detail', kwargs={'pk': log.id})
    update_data = {'action': 'update'}
    response = client.json.patch(url, data=json.dumps(update_data))
    assert response.status_code in [405, 403]  # Method not allowed or Forbidden

    # Try to delete
    response = client.delete(url)
    assert response.status_code in [405, 403]  # Method not allowed or Forbidden


def test_unauthenticated_user_cannot_access_audit_logs(client):
    """
    Given: A user is not authenticated
    When: They try to access audit logs
    Then: They should receive an authentication error
    """
    url = reverse('audit-logs-list')
    response = client.get(url)
    assert response.status_code in [401, 403]
