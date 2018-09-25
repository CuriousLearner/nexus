# Standard Library
import uuid

# Third Party Stuff
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import CIEmailField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
from phonenumber_field.modelfields import PhoneNumberField

# nexus Stuff
from nexus.base.models import UUIDModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str, is_staff: bool, is_superuser: bool, **extra_fields):
        """Creates and saves a User with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class User(AbstractBaseUser, UUIDModel, PermissionsMixin):

    GENDER_CHOICES = Choices(
        ('NOT_SELECTED', 'not_selected', _('Not Selected')),
        ('MALE', 'male', _('Male')),
        ('FEMALE', 'female', _('Female')),
        ('OTHERS', 'others', _('Others')),
    )

    TSHIRT_SIZE_CHOICES = Choices(
        ('NOT_SELECTED', 'not_selected', _('Not Selected')),
        ('SMALL', 'small', _('Small')),
        ('MEDIUM', 'medium', _('Medium')),
        ('LARGE', 'large', _('Large')),
        ('EXTRA_LARGE', 'extra_large', _('Extra Large')),
        ('DOUBLE_EXTRA_LARGE', 'extra_extra_large', _('Extra Extra Large')),
    )

    first_name = models.CharField(_('First Name'), null=False, blank=True, max_length=120)
    last_name = models.CharField(_('Last Name'), null=False, blank=True, max_length=120)
    # https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/fields/#citext-fields
    email = CIEmailField(_('Email Address'), unique=True, db_index=True)
    is_staff = models.BooleanField(
        _('Staff Status'), default=False,
        help_text='Designates whether the user can log into this admin site.')

    is_active = models.BooleanField('Active', default=True,
                                    help_text='Designates whether this user should be treated as '
                                              'active. Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField(_('Date Of Joining'), default=timezone.now, null=False, blank=False)

    gender = models.CharField(
        _('Gender'), default=GENDER_CHOICES.NOT_SELECTED,
        choices=GENDER_CHOICES, null=False, blank=False, max_length=12
    )
    tshirt_size = models.CharField(_('Tshirt Size'), default=TSHIRT_SIZE_CHOICES.NOT_SELECTED,
                                   choices=TSHIRT_SIZE_CHOICES, null=False, blank=False, max_length=30)
    phone_number = PhoneNumberField(_('Phone Number'), default='', null=False, blank=True, max_length=13)
    ticket_id = models.UUIDField(_('Ticket Id'), default=uuid.uuid4, null=False, blank=False)
    is_core_organizer = models.BooleanField(_('User is core_organizer'), default=False, null=False, blank=True,
                                            help_text='Designates whether this user is a Core Organizer')
    is_volunteer = models.BooleanField(_('User is volunteer'), default=False, null=False, blank=True,
                                       help_text='Designates whether this user is a Volunteer')

    USERNAME_FIELD = 'email'
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined', )

    def __str__(self):
        return str(self.id)

    def get_full_name(self) -> str:
        """Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self) -> str:
        """Returns the short name for the user.
        """
        return self.first_name.strip()
