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

    GENDER = Choices(
        ('MALE', 'M', _('male')),
        ('FEMALE', 'F', _('female')),
        ('OTHERS', 'O', _('others')),
    )

    TSHIRT_SIZE = Choices(
        ('SMALL', 'S', _('small')),
        ('MEDIUM', 'M', _('medium')),
        ('LARGE', 'L', _('large')),
        ('EXTRA_LARGE', 'XL', _('extra_large')),
        ('DOUBLE_EXTRA_LARGE', 'XXL', _('double extra large')),
    )

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

    gender = models.CharField(_('Gender'), default='O', choices=GENDER, max_length=6)
    tshirt_size = models.CharField(_('Tshirt Size'), default='L', choices=TSHIRT_SIZE, max_length=10)
    phone_number = PhoneNumberField(_('Phone Number'), blank=False, null=True, max_length=13)
    ticket_id = models.CharField(_('Ticket Id'), default=_('Not assigned'), blank=False, null=False, max_length=32)
    is_core_organizer = models.BooleanField(_('core organizer status'), default=False,
                                            help_text='Is the user a core organizer')
    is_volunteer = models.BooleanField(_('volunteer status'), default=False, help_text='Is the user a volunteer')

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
