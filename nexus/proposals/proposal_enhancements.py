# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class ProposalCategory(TimeStampedUUIDModel):
    """Categories for organizing proposals"""

    name = models.CharField(_('Category Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    color_code = models.CharField(_('Color Code'), max_length=7, default='#3498db')

    # Settings
    is_active = models.BooleanField(_('Is Active'), default=True)
    display_order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Proposal Category')
        verbose_name_plural = _('Proposal Categories')
        db_table = 'proposal_categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class CallForProposals(TimeStampedUUIDModel):
    """Call for Proposals (CFP) management"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('reviewing', 'Reviewing'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(_('CFP Title'), max_length=200)
    description = models.TextField(_('Description'))

    # Event relation
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             null=True, blank=True,
                             related_name='cfps', verbose_name=_('Event'))

    # Timing
    opens_at = models.DateTimeField(_('Opens At'))
    closes_at = models.DateTimeField(_('Closes At'))
    notification_date = models.DateField(_('Notification Date'), null=True, blank=True)

    # Categories
    categories = models.ManyToManyField(ProposalCategory, related_name='cfps',
                                       verbose_name=_('Accepted Categories'))

    # Requirements
    min_duration_minutes = models.PositiveIntegerField(_('Min Duration (minutes)'), default=30)
    max_duration_minutes = models.PositiveIntegerField(_('Max Duration (minutes)'), default=60)
    allowed_formats = models.JSONField(_('Allowed Formats'), default=list,
                                      help_text='e.g., talk, workshop, panel')

    # Submission limits
    max_submissions_per_speaker = models.PositiveIntegerField(_('Max Submissions Per Speaker'),
                                                              default=3)

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='draft')

    # Statistics
    total_submissions = models.PositiveIntegerField(_('Total Submissions'), default=0)
    accepted_count = models.PositiveIntegerField(_('Accepted Count'), default=0)
    rejected_count = models.PositiveIntegerField(_('Rejected Count'), default=0)

    class Meta:
        verbose_name = _('Call for Proposals')
        verbose_name_plural = _('Calls for Proposals')
        db_table = 'cfps'
        ordering = ['-opens_at']

    def __str__(self):
        return self.title


class SpeakerProfile(TimeStampedUUIDModel):
    """Enhanced speaker profiles"""

    user = models.OneToOneField('users.User', on_delete=models.CASCADE,
                               related_name='speaker_profile',
                               verbose_name=_('User'))

    # Bio
    bio = models.TextField(_('Bio'), max_length=500)
    short_bio = models.TextField(_('Short Bio'), max_length=140, blank=True,
                                 help_text='Twitter-length bio')

    # Professional info
    job_title = models.CharField(_('Job Title'), max_length=200, blank=True)
    company = models.CharField(_('Company'), max_length=200, blank=True)
    website = models.URLField(_('Website'), blank=True)

    # Social media
    twitter_handle = models.CharField(_('Twitter Handle'), max_length=100, blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    github_username = models.CharField(_('GitHub Username'), max_length=100, blank=True)

    # Speaking experience
    years_speaking = models.PositiveIntegerField(_('Years of Speaking Experience'), default=0)
    previous_talks_count = models.PositiveIntegerField(_('Previous Talks'), default=0)
    areas_of_expertise = models.JSONField(_('Areas of Expertise'), default=list)

    # Media
    profile_photo = models.ImageField(_('Profile Photo'), upload_to='speaker_photos/',
                                     null=True, blank=True)
    video_reel_url = models.URLField(_('Video Reel URL'), blank=True,
                                    help_text='Link to speaking video samples')

    # Preferences
    available_for_qa = models.BooleanField(_('Available for Q&A'), default=True)
    needs_travel_support = models.BooleanField(_('Needs Travel Support'), default=False)
    dietary_requirements = models.TextField(_('Dietary Requirements'), blank=True)
    accessibility_requirements = models.TextField(_('Accessibility Requirements'), blank=True)

    # Statistics
    total_proposals = models.PositiveIntegerField(_('Total Proposals'), default=0)
    accepted_proposals = models.PositiveIntegerField(_('Accepted Proposals'), default=0)
    avg_rating = models.FloatField(_('Average Rating'), default=0.0)

    class Meta:
        verbose_name = _('Speaker Profile')
        verbose_name_plural = _('Speaker Profiles')
        db_table = 'speaker_profiles'
        ordering = ['-accepted_proposals']

    def __str__(self):
        return f'{self.user.get_full_name()} - Speaker Profile'


class ProposalFeedback(TimeStampedUUIDModel):
    """Feedback on proposals"""

    FEEDBACK_TYPE_CHOICES = [
        ('organizer', 'Organizer Feedback'),
        ('reviewer', 'Reviewer Feedback'),
        ('public', 'Public Comment'),
    ]

    proposal = models.ForeignKey('proposals.Proposal', on_delete=models.CASCADE,
                                related_name='feedback', verbose_name=_('Proposal'))

    # Feedback details
    feedback_type = models.CharField(_('Feedback Type'), max_length=20,
                                    choices=FEEDBACK_TYPE_CHOICES)
    feedback_text = models.TextField(_('Feedback'))

    # Author
    author = models.ForeignKey('users.User', on_delete=models.CASCADE,
                              verbose_name=_('Author'))

    # Visibility
    is_public = models.BooleanField(_('Is Public'), default=False)
    visible_to_speaker = models.BooleanField(_('Visible to Speaker'), default=True)

    # Metadata
    is_actionable = models.BooleanField(_('Is Actionable'), default=False,
                                       help_text='Requires speaker action')
    is_resolved = models.BooleanField(_('Is Resolved'), default=False)

    class Meta:
        verbose_name = _('Proposal Feedback')
        verbose_name_plural = _('Proposal Feedback')
        db_table = 'proposal_feedback'
        ordering = ['-created_at']

    def __str__(self):
        return f'Feedback on {self.proposal.title} by {self.author.email}'


class ProposalTag(TimeStampedUUIDModel):
    """Tags for proposals"""

    name = models.CharField(_('Tag Name'), max_length=50, unique=True)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'), blank=True)

    # Usage
    usage_count = models.PositiveIntegerField(_('Usage Count'), default=0)

    class Meta:
        verbose_name = _('Proposal Tag')
        verbose_name_plural = _('Proposal Tags')
        db_table = 'proposal_tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProposalVersion(TimeStampedUUIDModel):
    """Version history for proposals"""

    proposal = models.ForeignKey('proposals.Proposal', on_delete=models.CASCADE,
                                related_name='versions', verbose_name=_('Proposal'))

    # Versioned content
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    outline = models.TextField(_('Outline'), blank=True)

    # Metadata
    version_number = models.PositiveIntegerField(_('Version Number'))
    change_summary = models.TextField(_('Change Summary'), blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  verbose_name=_('Created By'))

    class Meta:
        verbose_name = _('Proposal Version')
        verbose_name_plural = _('Proposal Versions')
        db_table = 'proposal_versions'
        ordering = ['proposal', '-version_number']
        unique_together = [['proposal', 'version_number']]

    def __str__(self):
        return f'{self.proposal.title} v{self.version_number}'


# Extend the existing Proposal model with new fields
def extend_proposal_model():
    """
    This function would be used to add new fields to the existing Proposal model
    via migration or model extension
    """
    additional_fields = {
        'category': models.ForeignKey(ProposalCategory, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='proposals',
                                     verbose_name=_('Category')),
        'cfp': models.ForeignKey(CallForProposals, on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='proposals',
                                verbose_name=_('CFP')),
        'tags': models.ManyToManyField(ProposalTag, related_name='proposals',
                                      blank=True, verbose_name=_('Tags')),
        'duration_minutes': models.PositiveIntegerField(_('Duration (minutes)'), default=45),
        'format': models.CharField(_('Format'), max_length=50,
                                  choices=[
                                      ('talk', 'Talk'),
                                      ('workshop', 'Workshop'),
                                      ('panel', 'Panel Discussion'),
                                      ('lightning', 'Lightning Talk'),
                                  ], default='talk'),
        'target_audience_level': models.CharField(_('Audience Level'), max_length=20,
                                                  choices=[
                                                      ('beginner', 'Beginner'),
                                                      ('intermediate', 'Intermediate'),
                                                      ('advanced', 'Advanced'),
                                                      ('all', 'All Levels'),
                                                  ], default='all'),
        'requires_av': models.BooleanField(_('Requires A/V'), default=True),
        'requires_internet': models.BooleanField(_('Requires Internet'), default=False),
        'version_number': models.PositiveIntegerField(_('Current Version'), default=1),
    }
    return additional_fields
