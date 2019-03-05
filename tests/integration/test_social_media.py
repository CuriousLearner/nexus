# Standard Library
import json

# Third Party Stuff
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from tests import factories as f
from tests import utils as u

# nexus Stuff
from nexus.social_media.models import Post

pytestmark = pytest.mark.django_db


def test_create_text_post(client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)
    scheduled_time = '2018-10-09T18:30:00Z'

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'fb',
        'scheduled_time': scheduled_time
    }
    response = client.json.post(url, json.dumps(post))
    expected_keys = [
        'is_posted', 'created_at', 'scheduled_time', 'id', 'posted_time',
        'text', 'is_approved', 'image', 'posted_at', 'modified_at',
        'posted_by', 'approval_time'
    ]
    assert set(expected_keys).issubset(response.data.keys())
    response_json = response.data
    assert response_json['posted_by'] == user.email
    assert response_json['text'] == post['text']
    assert response_json['posted_at'] == post['posted_at']
    assert response_json['scheduled_time'] == scheduled_time


def test_create_image_post(client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'fb',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }
    response = client.json.post(url, json.dumps(post))

    assert response.status_code == 201
    post_id = response.data['id']

    # Request upload image without providing any image
    url = reverse('posts-upload-image', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 400

    image = u.create_image(None, 'avatar.png')
    image = SimpleUploadedFile('front.png', image.getvalue())
    url = reverse('posts-upload-image', kwargs={'pk': post_id})
    response = client.post(url, {'image': image}, format='multipart')
    assert response.status_code == 200
    assert response.data["image"] is not None


def test_delete_image(client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'fb',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }
    response = client.json.post(url, json.dumps(post))

    assert response.status_code == 201
    post_id = response.data['id']

    # Delete image before uploading
    url = reverse('posts-delete-image', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 400

    image = u.create_image(None, 'avatar.png')
    image = SimpleUploadedFile('front.png', image.getvalue())
    url = reverse('posts-upload-image', kwargs={'pk': post_id})
    response = client.post(url, {'image': image}, format='multipart')
    assert response.status_code == 200
    assert response.data["image"] is not None

    url = reverse('posts-delete-image', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 200
    assert response.data["image"] is None


def test_post_approved_api(client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'fb',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }
    response = client.json.post(url, json.dumps(post))
    assert response.status_code == 201
    post_id = response.data['id']

    # Check that a normal user is not able to approve post
    non_core_organizer = f.create_user(email='non_core@example.com', password='test')
    client.login(user=non_core_organizer)
    url = reverse('posts-approve', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 403

    core_organizer = f.create_user(is_core_organizer=True)
    client.login(user=core_organizer)
    url = reverse('posts-approve', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 200
    assert response.data['is_approved'] is True
    assert response.data['approval_time']

    # If post is already approved
    url = reverse('posts-approve', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 200
    assert response.data['is_approved'] is True


def test_post_unapprove_api(client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'fb',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }
    response = client.json.post(url, json.dumps(post))
    assert response.status_code == 201
    post_id = response.data['id']

    # Check that a normal user is not able to unapprove the post
    non_core_organizer = f.create_user(email='non_core@example.com', password='test')
    client.login(user=non_core_organizer)
    url = reverse('posts-unapprove', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 403

    core_organizer = f.create_user(is_core_organizer=True)
    client.login(user=core_organizer)

    # Check that unapproving a post that has not been approved yet gives error
    url = reverse('posts-unapprove', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 400
    assert response.data['error_message'] == 'Post has not been approved yet'

    # Check to unapprove a post that has been approved
    url = reverse('posts-approve', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 200
    assert response.data['is_approved'] is True
    assert response.data['approval_time'] is not None

    url = reverse('posts-unapprove', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 200
    assert response.data['is_approved'] is False
    assert response.data['approval_time'] is None

    # Check that unapproving a post that has already been published gives error
    Post.objects.filter(pk=post_id).update(is_approved=True, is_posted=True)
    url = reverse('posts-unapprove', kwargs={'pk': post_id})
    response = client.post(url)
    assert response.status_code == 400
    assert response.data['error_message'] == 'Can not unapprove, post has already been published'


def test_staff_post_edit(client):
    user = f.create_user(email='test@example.com', password='test')
    client.login(user=user)

    url = reverse('posts-list')
    post = {
        'text': 'Announcement!',
        'posted_at': 'fb',
        'scheduled_time': '2018-10-09T18:30:00Z'
    }
    response = client.json.post(url, json.dumps(post))
    assert response.status_code == 201
    post_id = response.data['id']

    user = f.create_user(email='staff@example.com', password='most_secure', is_staff=True)
    client.login(user=user)
    url = reverse('posts-detail', kwargs={'pk': post_id})
    data = {
        'text': 'Edited announcement',
    }
    response = client.json.patch(url, json.dumps(data))
    assert response.status_code == 200
    assert response.data["text"] == "Edited announcement"
