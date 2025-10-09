"""
Helpers to create dynamic model instances for testing purposes.

Usages:
>>> from tests import factories as f
>>>
>>> user = f.create_user(first_name="Robert", last_name="Downey")  # creates single instance of user
>>> users = f.create_user(n=5, is_active=False)  # creates 5 instances of user

There is a bit of magic going on behind the scenes with `G` method from https://django-dynamic-fixture.readthedocs.io/
"""

# Third Party Stuff
from django.apps import apps
from django.conf import settings
from django_dynamic_fixture import G


def create_user(**kwargs):
    """Create an user along with their dependencies."""
    User = apps.get_model(settings.AUTH_USER_MODEL)
    user = G(User, **kwargs)
    user.set_password(kwargs.get('password', 'test'))
    user.save()
    return user


def create_proposal(**kwargs):
    return G(apps.get_model('proposals.Proposal'), **kwargs)


def create_proposal_kind(**kwargs):
    return G(apps.get_model('proposals.ProposalKind'), **kwargs)


def create_post(**kwargs):
    return G(apps.get_model('social_media.Post'), **kwargs)


# Events factories
def create_event(**kwargs):
    return G(apps.get_model('events.Event'), **kwargs)


def create_venue(**kwargs):
    return G(apps.get_model('events.Venue'), **kwargs)


def create_session(**kwargs):
    return G(apps.get_model('events.Session'), **kwargs)


def create_attendee(**kwargs):
    return G(apps.get_model('events.Attendee'), **kwargs)


def create_sponsor(**kwargs):
    return G(apps.get_model('events.Sponsor'), **kwargs)


# Volunteers factories
def create_volunteer_role(**kwargs):
    return G(apps.get_model('volunteers.VolunteerRole'), **kwargs)


def create_volunteer_shift(**kwargs):
    return G(apps.get_model('volunteers.VolunteerShift'), **kwargs)


def create_volunteer_assignment(**kwargs):
    return G(apps.get_model('volunteers.VolunteerAssignment'), **kwargs)


def create_volunteer_task(**kwargs):
    return G(apps.get_model('volunteers.VolunteerTask'), **kwargs)


def create_volunteer_hours(**kwargs):
    return G(apps.get_model('volunteers.VolunteerHours'), **kwargs)


# Audit factories
def create_audit_log(**kwargs):
    return G(apps.get_model('base.AuditLog'), **kwargs)
