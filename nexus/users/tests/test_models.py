# Third Party Stuff
from django.test import TestCase

# nexus Stuff
from nexus.users.models import User


class UserModelTestCase(TestCase):

    def test_create_user(self):
        u = User.objects.create_user(
            email='f@f.com', password='abc', first_name="F", last_name='B',
            gender='others', tshirt_size='large', phone_number='+910123456789'
        )
        assert u.is_active is True
        assert u.is_staff is False
        assert u.is_superuser is False
        assert u.email == 'f@f.com'
        assert u.get_full_name() == 'F B'
        assert u.get_short_name() == 'F'
        assert str(u) == str('{} - {}'.format(u.email, u.get_full_name()))
        assert u.gender == User.GENDER_CHOICES.OTHERS
        assert u.tshirt_size == User.TSHIRT_SIZE_CHOICES.LARGE
        assert u.is_core_organizer is False
        assert u.is_volunteer is False
        assert u.phone_number == '+910123456789'

    def test_create_super_user(self):
        u = User.objects.create_superuser(email='f@f.com', password='abc')
        assert u.is_active is True
        assert u.is_staff is True
        assert u.is_superuser is True
        assert str(u) == str('{} - {}'.format(u.email, u.get_full_name()))
