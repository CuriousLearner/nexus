# Third Party Stuff
from rest_framework import serializers

from . import models


class AdminPostSerializer(serializers.ModelSerializer):
    posted_by = serializers.EmailField(source='posted_by.email', read_only=True)

    def create(self, validated_data):
        from nexus.social_media import url_shortener
        from nexus.social_media.tasks import process_post_hashtags_task

        posted_by = self.context['request'].user
        validated_data['posted_by'] = posted_by

        # Auto-shorten URLs if text contains URLs
        if validated_data.get('text'):
            validated_data['text'] = url_shortener.extract_and_shorten_urls(
                validated_data['text']
            )

        post = models.Post.objects.create(**validated_data)

        # Process hashtags asynchronously
        process_post_hashtags_task.delay(str(post.id))

        return post

    class Meta:
        model = models.Post
        fields = ['id', 'created_at', 'modified_at', 'posted_by', 'scheduled_time',
                  'approval_time', 'posted_time', 'posted_at', 'platforms', 'image', 'video', 'text',
                  'is_approved', 'is_posted', 'is_draft', 'use_platform_schedules']
        read_only_fields = ['created_at', 'modified_at']


class PlatformScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlatformSchedule
        fields = ['id', 'post', 'platform', 'scheduled_time', 'is_posted', 'posted_time', 'error_message']
        read_only_fields = ['is_posted', 'posted_time']


class PostSerializer(AdminPostSerializer):
    class Meta(AdminPostSerializer.Meta):
        read_only_fields = AdminPostSerializer.Meta.read_only_fields + [
            'is_approved', 'is_posted', 'approval_time', 'posted_time']
