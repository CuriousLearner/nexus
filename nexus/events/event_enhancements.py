# Standard Library
import secrets
import string

# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class TicketType(TimeStampedUUIDModel):
    """Ticket types for events"""

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             related_name='ticket_types', verbose_name=_('Event'))

    # Ticket details
    name = models.CharField(_('Ticket Name'), max_length=200,
                           help_text='e.g., Early Bird, VIP, Student')
    description = models.TextField(_('Description'), blank=True)

    # Pricing
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=3, default='USD')

    # Availability
    quantity_total = models.PositiveIntegerField(_('Total Quantity'))
    quantity_sold = models.PositiveIntegerField(_('Quantity Sold'), default=0)
    quantity_reserved = models.PositiveIntegerField(_('Quantity Reserved'), default=0)

    # Timing
    sales_start = models.DateTimeField(_('Sales Start'))
    sales_end = models.DateTimeField(_('Sales End'))

    # Restrictions
    min_per_order = models.PositiveIntegerField(_('Minimum Per Order'), default=1)
    max_per_order = models.PositiveIntegerField(_('Maximum Per Order'), default=10)
    requires_approval = models.BooleanField(_('Requires Approval'), default=False)

    # Settings
    is_active = models.BooleanField(_('Is Active'), default=True)
    display_order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Ticket Type')
        verbose_name_plural = _('Ticket Types')
        db_table = 'ticket_types'
        ordering = ['event', 'display_order']

    def __str__(self):
        return f'{self.event.name} - {self.name}'

    @property
    def quantity_available(self):
        """Calculate available tickets"""
        return self.quantity_total - self.quantity_sold - self.quantity_reserved

    @property
    def is_sold_out(self):
        """Check if sold out"""
        return self.quantity_available <= 0


class Ticket(TimeStampedUUIDModel):
    """Individual tickets"""

    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('used', 'Used/Checked In'),
    ]

    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE,
                                   related_name='tickets', verbose_name=_('Ticket Type'))
    attendee = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                related_name='tickets', verbose_name=_('Attendee'))

    # Ticket identification
    ticket_number = models.CharField(_('Ticket Number'), max_length=20, unique=True,
                                    db_index=True)
    qr_code = models.CharField(_('QR Code'), max_length=100, unique=True, db_index=True)

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='pending')

    # Payment
    payment_amount = models.DecimalField(_('Payment Amount'), max_digits=10,
                                        decimal_places=2)
    payment_reference = models.CharField(_('Payment Reference'), max_length=200, blank=True)
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)

    # Check-in
    checked_in = models.BooleanField(_('Checked In'), default=False)
    checked_in_at = models.DateTimeField(_('Checked In At'), null=True, blank=True)
    checked_in_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='checked_in_tickets',
                                     verbose_name=_('Checked In By'))

    # Notes
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        db_table = 'tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_type', 'status']),
            models.Index(fields=['attendee']),
        ]

    def __str__(self):
        return f'{self.ticket_number} - {self.attendee.email}'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        if not self.qr_code:
            self.qr_code = self.generate_qr_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_ticket_number():
        """Generate unique ticket number"""
        prefix = 'TKT'
        random_part = ''.join(secrets.choice(string.digits) for _ in range(8))
        return f'{prefix}{random_part}'

    @staticmethod
    def generate_qr_code():
        """Generate unique QR code"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))


class EventWaitlist(TimeStampedUUIDModel):
    """Waitlist for sold-out events"""

    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('notified', 'Notified'),
        ('converted', 'Converted to Ticket'),
        ('expired', 'Expired'),
    ]

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             related_name='waitlist_entries', verbose_name=_('Event'))
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE,
                                   null=True, blank=True,
                                   related_name='waitlist_entries',
                                   verbose_name=_('Preferred Ticket Type'))

    # User details
    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='waitlist_entries', verbose_name=_('User'))

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='waiting')
    position = models.PositiveIntegerField(_('Position'), default=0)

    # Notifications
    notified_at = models.DateTimeField(_('Notified At'), null=True, blank=True)
    notification_expires_at = models.DateTimeField(_('Notification Expires At'),
                                                   null=True, blank=True)

    # Conversion
    converted_ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        verbose_name=_('Converted Ticket'))

    class Meta:
        verbose_name = _('Event Waitlist Entry')
        verbose_name_plural = _('Event Waitlist Entries')
        db_table = 'event_waitlist'
        ordering = ['event', 'position', 'created_at']
        unique_together = [['event', 'user']]

    def __str__(self):
        return f'{self.user.email} - {self.event.name} (Position {self.position})'


class EventReminder(TimeStampedUUIDModel):
    """Email reminders for events"""

    REMINDER_TYPE_CHOICES = [
        ('registration_confirmation', 'Registration Confirmation'),
        ('pre_event', 'Pre-Event Reminder'),
        ('day_before', 'Day Before Event'),
        ('day_of', 'Day of Event'),
        ('post_event', 'Post-Event Follow-up'),
    ]

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             related_name='reminders', verbose_name=_('Event'))

    # Reminder details
    reminder_type = models.CharField(_('Reminder Type'), max_length=50,
                                    choices=REMINDER_TYPE_CHOICES)
    subject = models.CharField(_('Email Subject'), max_length=200)
    message = models.TextField(_('Email Message'),
                              help_text='Use {{name}}, {{event_name}}, {{date}} etc. for personalization')

    # Timing
    send_days_before = models.IntegerField(_('Send Days Before Event'), default=1,
                                          help_text='Negative for post-event')
    send_time = models.TimeField(_('Send Time'))

    # Status
    is_active = models.BooleanField(_('Is Active'), default=True)
    last_sent_at = models.DateTimeField(_('Last Sent At'), null=True, blank=True)
    total_sent = models.PositiveIntegerField(_('Total Sent'), default=0)

    class Meta:
        verbose_name = _('Event Reminder')
        verbose_name_plural = _('Event Reminders')
        db_table = 'event_reminders'
        ordering = ['event', 'send_days_before']

    def __str__(self):
        return f'{self.event.name} - {self.get_reminder_type_display()}'


class Certificate(TimeStampedUUIDModel):
    """Certificates for event participation"""

    CERTIFICATE_TYPE_CHOICES = [
        ('attendance', 'Certificate of Attendance'),
        ('completion', 'Certificate of Completion'),
        ('speaker', 'Speaker Certificate'),
        ('volunteer', 'Volunteer Certificate'),
    ]

    # Event/User
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             related_name='certificates', verbose_name=_('Event'))
    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='certificates', verbose_name=_('User'))

    # Certificate details
    certificate_type = models.CharField(_('Certificate Type'), max_length=20,
                                       choices=CERTIFICATE_TYPE_CHOICES)
    certificate_number = models.CharField(_('Certificate Number'), max_length=50,
                                         unique=True, db_index=True)

    # Template
    template_name = models.CharField(_('Template Name'), max_length=100, default='default')
    custom_text = models.TextField(_('Custom Text'), blank=True,
                                   help_text='Additional text to include on certificate')

    # Generation
    generated_at = models.DateTimeField(_('Generated At'), auto_now_add=True)
    generated_pdf = models.FileField(_('PDF File'), upload_to='certificates/',
                                    null=True, blank=True)

    # Verification
    verification_code = models.CharField(_('Verification Code'), max_length=20,
                                        unique=True, db_index=True)
    is_verified = models.BooleanField(_('Is Verified'), default=False)

    # Tracking
    downloaded_count = models.PositiveIntegerField(_('Downloaded Count'), default=0)
    last_downloaded_at = models.DateTimeField(_('Last Downloaded At'),
                                             null=True, blank=True)

    class Meta:
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
        db_table = 'certificates'
        ordering = ['-generated_at']
        unique_together = [['event', 'user', 'certificate_type']]

    def __str__(self):
        return f'{self.certificate_number} - {self.user.email}'

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_certificate_number():
        """Generate unique certificate number"""
        prefix = 'CERT'
        random_part = ''.join(secrets.choice(string.digits) for _ in range(10))
        return f'{prefix}{random_part}'

    @staticmethod
    def generate_verification_code():
        """Generate verification code"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))


class EventWebsite(TimeStampedUUIDModel):
    """Event website builder"""

    event = models.OneToOneField('events.Event', on_delete=models.CASCADE,
                                related_name='website', verbose_name=_('Event'))

    # URL
    slug = models.SlugField(_('URL Slug'), unique=True)
    custom_domain = models.CharField(_('Custom Domain'), max_length=200, blank=True)

    # Design
    theme = models.CharField(_('Theme'), max_length=50, default='default')
    primary_color = models.CharField(_('Primary Color'), max_length=7, default='#3498db')
    logo = models.ImageField(_('Logo'), upload_to='event_websites/', null=True, blank=True)
    banner_image = models.ImageField(_('Banner Image'), upload_to='event_websites/',
                                    null=True, blank=True)

    # Content sections
    show_speakers = models.BooleanField(_('Show Speakers Section'), default=True)
    show_schedule = models.BooleanField(_('Show Schedule Section'), default=True)
    show_sponsors = models.BooleanField(_('Show Sponsors Section'), default=True)
    show_venue = models.BooleanField(_('Show Venue Information'), default=True)

    custom_sections = models.JSONField(_('Custom Sections'), default=list,
                                      help_text='Additional custom content sections')

    # SEO
    meta_title = models.CharField(_('Meta Title'), max_length=200, blank=True)
    meta_description = models.TextField(_('Meta Description'), blank=True)

    # Settings
    is_published = models.BooleanField(_('Is Published'), default=False)
    require_login = models.BooleanField(_('Require Login'), default=False)

    # Analytics
    page_views = models.PositiveIntegerField(_('Page Views'), default=0)
    unique_visitors = models.PositiveIntegerField(_('Unique Visitors'), default=0)

    class Meta:
        verbose_name = _('Event Website')
        verbose_name_plural = _('Event Websites')
        db_table = 'event_websites'

    def __str__(self):
        return f'Website for {self.event.name}'

    @property
    def full_url(self):
        """Get full website URL"""
        if self.custom_domain:
            return f'https://{self.custom_domain}'
        return f'https://events.example.com/{self.slug}'
