# Third Party Stuff
import django_filters

# Nexus Stuff
from nexus.users.models import User


class UserFilter(django_filters.FilterSet):
    """Filter for User model to enable searching and filtering"""

    email = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=User.GENDER_CHOICES)
    tshirt_size = django_filters.ChoiceFilter(choices=User.TSHIRT_SIZE_CHOICES)
    is_core_organizer = django_filters.BooleanFilter()
    is_volunteer = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ['gender', 'tshirt_size', 'is_core_organizer', 'is_volunteer', 'is_active', 'is_staff']
