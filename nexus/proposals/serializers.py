from rest_framework import serializers

from . import models


class ProposalSerializer(serializers.ModelSerializer):

    speaker = serializers.EmailField(source='posted_by.email', read_only=True)

    class Meta:
        model = models.Proposal
        fields = ('id', 'title', 'speaker', 'kind', 'level', 'duration', 'abstract', 'description')
        read_only_fields = ('submitted_at', 'approved_at', 'modified_at', 'status')

    def create(self, validated_data):
        speaker = self.context['request'].user
        validated_data['speaker'] = speaker
        return models.Proposal.objects.create(**validated_data)
