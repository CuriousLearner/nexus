# Third Party Stuff
from rest_framework import serializers

from . import models


class AdminPostSerializer(serializers.ModelSerializer):
    posted_by = serializers.EmailField(source='posted_by.email', read_only=True)

    def create(self, validated_data):
        posted_by = self.context['request'].user
        validated_data['posted_by'] = posted_by
        return models.Post.objects.create(**validated_data)

    class Meta:
        model = models.Post
        fields = ['id', 'created_at', 'modified_at', 'posted_by', 'scheduled_time',
                  'approval_time', 'posted_time', 'posted_at', 'image', 'text',
                  'is_approved', 'is_posted']
        read_only_fields = ['created_at', 'modified_at']


class PostSerializer(AdminPostSerializer):
    class Meta(AdminPostSerializer.Meta):
        read_only_fields = AdminPostSerializer.Meta.read_only_fields + [
            'is_approved', 'is_posted', 'approval_time', 'posted_time']
