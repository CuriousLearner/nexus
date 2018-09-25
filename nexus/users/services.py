# Third Party Stuff
from django.contrib.auth import get_user_model, authenticate

# nexus Stuff
from nexus.base import exceptions as exc


def get_and_authenticate_user(email, password):
    user = authenticate(username=email, password=password)
    if user is None:
        raise exc.WrongArguments("Invalid username/password. Please try again!")

    return user


def create_user_account(email, password, first_name="", last_name="", **extra_fields):
    user = get_user_model().objects.create_user(
        email=email, password=password, first_name=first_name, last_name=last_name, **extra_fields)
    return user


def get_user_by_email(email: str):
    return get_user_model().objects.filter(email__iexact=email).first()
