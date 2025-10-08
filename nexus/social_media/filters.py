# Third Party Stuff
import django_filters
from django.db import models

# Nexus Stuff
from nexus.social_media.models import Post


class PostFilter(django_filters.FilterSet):
    """Filter for Post model to enable searching and filtering"""

    text = django_filters.CharFilter(lookup_expr='icontains')
    posted_at = django_filters.ChoiceFilter(choices=(
        ('fb', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'Linkedin')
    ))
    is_approved = django_filters.BooleanFilter()
    is_posted = django_filters.BooleanFilter()
    is_draft = django_filters.BooleanFilter()
    scheduled_time_after = django_filters.DateTimeFilter(field_name='scheduled_time', lookup_expr='gte')
    scheduled_time_before = django_filters.DateTimeFilter(field_name='scheduled_time', lookup_expr='lte')
    posted_by = django_filters.CharFilter(field_name='posted_by__email', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['posted_at', 'is_approved', 'is_posted', 'is_draft']
