from rest_framework import serializers

from nexus.proposals import models


class ProposalSerializer(serializers.ModelSerializer):
    speaker = serializers.EmailField(source='speaker.email', read_only=True)

    class Meta:
        model = models.Proposal
        fields = ('id', 'title', 'speaker', 'status', 'kind', 'level',
                  'duration', 'abstract', 'description', 'submitted_at',
                  'approved_at', 'modified_at')
        read_only_fields = ('submitted_at', 'approved_at', 'modified_at', 'status')

    def create(self, validated_data):
        speaker = self.context['request'].user
        validated_data['speaker'] = speaker
        return models.Proposal.objects.create(**validated_data)
