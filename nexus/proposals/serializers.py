# Third Party Stuff
from rest_framework import serializers

# nexus Stuff
from nexus.proposals import models


def _get_user_from_context(context):
    if 'user' in context:
        return context['user']
    if 'request' in context:
        return context['request'].user
    return None


class ProposalSerializer(serializers.ModelSerializer):
    speaker = serializers.EmailField(source='speaker__email', read_only=True)

    class Meta:
        model = models.Proposal
        fields = (
            'id', 'title', 'speaker', 'status', 'kind', 'level', 'duration',
            'abstract', 'description', 'submitted_at', 'approved_at',
            'modified_at',
        )
        read_only_fields = (
            'id', 'submitted_at', 'approved_at', 'modified_at', 'status',
        )

    def create(self, validated_data):
        speaker = _get_user_from_context(self.context)
        validated_data['speaker'] = speaker
        return models.Proposal.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            instance['k'] = v
        instance.save()
        return instance
