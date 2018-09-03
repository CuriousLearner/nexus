# Third Party Stuff
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import CIEmailField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices

# nexus Stuff
from nexus.base.models import UUIDModel


GENDER = Choices(
    ('MALE', 'M', _('Male')),
    ('FEMALE', 'F', _('Female')),
    ('OTHERS', 'O', _('Others')),
)

TSHIRT_SIZE = Choices(
    ('SMALL', 'S', _('Small')),
    ('MEDIUM', 'M', _('Medium')),
    ('LARGE', 'L', _('Large')),
    ('EXTRA_LARGE', 'XL', _('Extra_Large')),
    ('DOUBLE_EXTRA_LARGE', 'XXL', _('Double Extra Large')),
)

USER_TYPE = Choices(
    ('ADMIN', 'ADM', _('Administrator')),
    ('VOLUNTEER', 'VOL', _('Volunteer')),
    ('ATTENDEE', 'ATT', _('Attendee')),
)


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
    first_name = models.CharField(_('First Name'), max_length=120, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=120, blank=True)
    # https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/fields/#citext-fields
    email = CIEmailField(_('email address'), unique=True, db_index=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text='Designates whether the user can log into this admin site.')

    is_active = models.BooleanField('active', default=True,
                                    help_text='Designates whether this user should be treated as '
                                              'active. Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    gender = models.CharField(_('Gender'), choices=GENDER, max_length=6)
    tshirt_size = models.CharField(_('Tshirt Size'), choices=TSHIRT_SIZE, max_length=10)
    contact = models.CharField(_('Contact'), blank=False, null=True, max_length=13)
    ticked_id = models.CharField(_('Ticket Id'), blank=False, null=False)
    user_type = models.CharField(_('User Role'), choices=USER_TYPE, max_length=13)

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
