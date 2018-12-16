# Python Stuff

# Third Party Stuff
from django.test import TestCase
from tests import factories as f

# nexus Stuff
from nexus.social_media.models import Post
from nexus.users.models import User


class TestPostModel(TestCase):

    def setUp(self):
        self.user = f.create_user(email='test@example.com', password='test')
        self.super_user = User.objects.create_superuser(email='super@user.com', password='superuser_pass')

    def test_create_post(self):
        post = {
            'posted_at': 'fb',
            'scheduled_time': '2018-10-10 00:00+05:30',
            'text': 'Happy 10th October from the community!',
            'posted_by': self.user
        }
        post = Post.objects.create(**post)
        assert post.id
        assert post.posted_at == 'fb'
        assert post.text == 'Happy 10th October from the community!'
        assert str(post.posted_by) == str(self.user)
        assert post.scheduled_time == '2018-10-10 00:00+05:30'
        assert not post.image._file
        assert not post.posted_time
        assert post.is_approved is False
        assert not post.approval_time
        assert str(post) == str(post.id)
