# Third Party Stuff
from rest_framework import serializers

# nexus Stuff
from nexus.proposals import models
from nexus.base.utils.serializer_utils import get_user_from_context


class CreateSerializer(serializers.Serializer):
    speaker = serializers.EmailField(source='speaker__email', read_only=True)

    def create(self, validated_data):
        speaker = get_user_from_context(self.context)
        validated_data['speaker'] = speaker
        return models.Proposal.objects.create(**validated_data)

    class Meta:
        model = models.Proposal
        fields = [
            'id', 'title', 'speaker', 'status', 'kind', 'level', 'duration',
            'abstract', 'description', 'submitted_at', 'approved_at',
            'modified_at',
        ]
        read_only_fields = [
            'id', 'submitted_at', 'approved_at', 'modified_at', 'status',
        ]


class StatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Proposal
        fields = CreateSerializer.Meta.fields + ['approved_at', 'status']

        read_only_fields = [
            'id', 'submitted_at', 'modified_at'
        ]
