# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _
from extended_choices import Choices

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class Event(TimeStampedUUIDModel):
    """Model to represent events/conferences"""

    STATUS_CHOICES = Choices(
        ('DRAFT', 'draft', _('Draft')),
        ('PUBLISHED', 'published', _('Published')),
        ('ONGOING', 'ongoing', _('Ongoing')),
        ('COMPLETED', 'completed', _('Completed')),
        ('CANCELLED', 'cancelled', _('Cancelled')),
    )

    name = models.CharField(_('Event Name'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True)
    description = models.TextField(_('Description'))
    tagline = models.CharField(_('Tagline'), max_length=300, blank=True)

    # Dates
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    registration_start = models.DateTimeField(_('Registration Start'))
    registration_end = models.DateTimeField(_('Registration End'))
    cfp_start = models.DateTimeField(_('CFP Start'), null=True, blank=True)
    cfp_end = models.DateTimeField(_('CFP End'), null=True, blank=True)

    # Location
    venue_name = models.CharField(_('Venue Name'), max_length=200, blank=True)
    venue_address = models.TextField(_('Venue Address'), blank=True)
    city = models.CharField(_('City'), max_length=100)
    country = models.CharField(_('Country'), max_length=100)
    is_virtual = models.BooleanField(_('Is Virtual'), default=False)
    virtual_platform = models.CharField(_('Virtual Platform'), max_length=100, blank=True,
                                       help_text='e.g., Zoom, Google Meet')

    # Metadata
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default=STATUS_CHOICES.DRAFT)
    max_attendees = models.PositiveIntegerField(_('Max Attendees'), null=True, blank=True)
    website_url = models.URLField(_('Website URL'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='event_logos/', null=True, blank=True)
    banner = models.ImageField(_('Banner'), upload_to='event_banners/', null=True, blank=True)

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        db_table = 'events'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Venue(TimeStampedUUIDModel):
    """Model to represent event venues/rooms"""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='venues',
                             verbose_name=_('Event'))
    name = models.CharField(_('Venue Name'), max_length=200)
    capacity = models.PositiveIntegerField(_('Capacity'))
    description = models.TextField(_('Description'), blank=True)
    floor = models.CharField(_('Floor'), max_length=50, blank=True)

    # Equipment
    has_projector = models.BooleanField(_('Has Projector'), default=True)
    has_microphone = models.BooleanField(_('Has Microphone'), default=True)
    has_whiteboard = models.BooleanField(_('Has Whiteboard'), default=False)
    additional_equipment = models.TextField(_('Additional Equipment'), blank=True)

    class Meta:
        verbose_name = _('Venue')
        verbose_name_plural = _('Venues')
        db_table = 'event_venues'
        ordering = ['event', 'name']

    def __str__(self):
        return f'{self.event.name} - {self.name}'


class Session(TimeStampedUUIDModel):
    """Model to represent event sessions/talks"""

    SESSION_TYPE_CHOICES = Choices(
        ('TALK', 'talk', _('Talk')),
        ('WORKSHOP', 'workshop', _('Workshop')),
        ('PANEL', 'panel', _('Panel Discussion')),
        ('KEYNOTE', 'keynote', _('Keynote')),
        ('LIGHTNING', 'lightning', _('Lightning Talk')),
        ('BREAK', 'break', _('Break')),
        ('SOCIAL', 'social', _('Social Event')),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sessions',
                             verbose_name=_('Event'))
    proposal = models.OneToOneField('proposals.Proposal', on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='session',
                                   verbose_name=_('Proposal'))
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='sessions',
                             verbose_name=_('Venue'))

    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    session_type = models.CharField(_('Session Type'), max_length=20,
                                   choices=SESSION_TYPE_CHOICES, default=SESSION_TYPE_CHOICES.TALK)

    # Timing
    start_time = models.DateTimeField(_('Start Time'))
    end_time = models.DateTimeField(_('End Time'))

    # Speakers
    speakers = models.ManyToManyField('users.User', related_name='sessions',
                                     verbose_name=_('Speakers'))

    # Recording
    is_recorded = models.BooleanField(_('Is Recorded'), default=True)
    recording_url = models.URLField(_('Recording URL'), blank=True)
    slides_url = models.URLField(_('Slides URL'), blank=True)

    class Meta:
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
        db_table = 'event_sessions'
        ordering = ['event', 'start_time']

    def __str__(self):
        return f'{self.event.name} - {self.title}'


class Attendee(TimeStampedUUIDModel):
    """Model to track event attendees/registrations"""

    STATUS_CHOICES = Choices(
        ('REGISTERED', 'registered', _('Registered')),
        ('CONFIRMED', 'confirmed', _('Confirmed')),
        ('CHECKED_IN', 'checked_in', _('Checked In')),
        ('CANCELLED', 'cancelled', _('Cancelled')),
        ('NO_SHOW', 'no_show', _('No Show')),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees',
                             verbose_name=_('Event'))
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='event_attendances',
                            verbose_name=_('User'))

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default=STATUS_CHOICES.REGISTERED)
    registration_date = models.DateTimeField(_('Registration Date'), auto_now_add=True)
    checked_in_at = models.DateTimeField(_('Checked In At'), null=True, blank=True)

    # Ticket info
    ticket_number = models.CharField(_('Ticket Number'), max_length=50, unique=True)
    ticket_type = models.CharField(_('Ticket Type'), max_length=100, blank=True,
                                  help_text='e.g., Early Bird, Regular, VIP')

    # Dietary/accessibility requirements
    dietary_requirements = models.TextField(_('Dietary Requirements'), blank=True)
    accessibility_requirements = models.TextField(_('Accessibility Requirements'), blank=True)
    special_requests = models.TextField(_('Special Requests'), blank=True)

    class Meta:
        verbose_name = _('Attendee')
        verbose_name_plural = _('Attendees')
        db_table = 'event_attendees'
        unique_together = [['event', 'user']]
        ordering = ['-registration_date']

    def __str__(self):
        return f'{self.user.email} - {self.event.name}'


class Sponsor(TimeStampedUUIDModel):
    """Model to track event sponsors"""

    TIER_CHOICES = Choices(
        ('PLATINUM', 'platinum', _('Platinum')),
        ('GOLD', 'gold', _('Gold')),
        ('SILVER', 'silver', _('Silver')),
        ('BRONZE', 'bronze', _('Bronze')),
        ('COMMUNITY', 'community', _('Community')),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sponsors',
                             verbose_name=_('Event'))
    name = models.CharField(_('Sponsor Name'), max_length=200)
    tier = models.CharField(_('Tier'), max_length=20, choices=TIER_CHOICES)
    logo = models.ImageField(_('Logo'), upload_to='sponsor_logos/', null=True, blank=True)
    website_url = models.URLField(_('Website URL'), blank=True)
    description = models.TextField(_('Description'), blank=True)

    # Contact
    contact_name = models.CharField(_('Contact Name'), max_length=200, blank=True)
    contact_email = models.EmailField(_('Contact Email'), blank=True)

    # Display order
    display_order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Sponsor')
        verbose_name_plural = _('Sponsors')
        db_table = 'event_sponsors'
        ordering = ['event', 'tier', 'display_order']

    def __str__(self):
        return f'{self.event.name} - {self.name} ({self.get_tier_display()})'
