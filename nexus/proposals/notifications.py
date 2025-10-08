# Third Party Stuff
from django.conf import settings
from django.template.loader import render_to_string
from mail_templated import EmailMessage

# Nexus Stuff
from nexus.proposals.models import Proposal


def send_proposal_submitted_notification(proposal):
    """Send email notification when a proposal is submitted"""
    context = {
        'proposal': proposal,
        'speaker_name': proposal.speaker.get_full_name(),
        'proposal_title': proposal.title,
    }

    message = EmailMessage(
        'emails/proposal_submitted.html',
        context,
        settings.DEFAULT_FROM_EMAIL,
        [proposal.speaker.email]
    )
    message.send()


def send_proposal_accepted_notification(proposal):
    """Send email notification when a proposal is accepted"""
    context = {
        'proposal': proposal,
        'speaker_name': proposal.speaker.get_full_name(),
        'proposal_title': proposal.title,
    }

    message = EmailMessage(
        'emails/proposal_accepted.html',
        context,
        settings.DEFAULT_FROM_EMAIL,
        [proposal.speaker.email]
    )
    message.send()


def send_proposal_rejected_notification(proposal):
    """Send email notification when a proposal is rejected/unaccepted"""
    context = {
        'proposal': proposal,
        'speaker_name': proposal.speaker.get_full_name(),
        'proposal_title': proposal.title,
    }

    message = EmailMessage(
        'emails/proposal_rejected.html',
        context,
        settings.DEFAULT_FROM_EMAIL,
        [proposal.speaker.email]
    )
    message.send()


def send_proposal_status_update_notification(proposal, old_status, new_status):
    """Send email notification when a proposal status changes"""

    if new_status == Proposal.STATUS_CHOICES.ACCEPTED:
        send_proposal_accepted_notification(proposal)
    elif new_status == Proposal.STATUS_CHOICES.UNACCEPTED and old_status == Proposal.STATUS_CHOICES.SUBMITTED:
        send_proposal_rejected_notification(proposal)
