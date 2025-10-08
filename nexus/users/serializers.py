from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ['id', 'first_name', 'last_name', 'email', 'gender', 'tshirt_size', 'ticket_id', 'phone_number',
                  'is_core_organizer', 'is_volunteer', 'date_joined', 'is_active', 'is_staff', 'is_superuser',
                  'profile_photo', 'bio', 'twitter_handle', 'linkedin_url', 'github_username', 'website']
        read_only_fields = ['id', 'ticket_id', 'is_core_organizer', 'is_volunteer', 'date_joined', 'is_active',
                            'is_staff', 'is_superuser']
