# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class VolunteerApplication(TimeStampedUUIDModel):
    """Application to become a volunteer"""

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='volunteer_applications',
                            verbose_name=_('User'))
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             null=True, blank=True,
                             related_name='volunteer_applications',
                             verbose_name=_('Event'))

    # Application details
    motivation = models.TextField(_('Motivation'),
                                  help_text='Why do you want to volunteer?')
    experience = models.TextField(_('Previous Experience'), blank=True)
    skills = models.JSONField(_('Skills'), default=list,
                             help_text='List of relevant skills')

    # Availability
    available_dates = models.JSONField(_('Available Dates'), default=list)
    hours_per_week = models.PositiveIntegerField(_('Hours Per Week'), default=0)

    # Preferences
    preferred_roles = models.ManyToManyField('volunteers.VolunteerRole',
                                            related_name='applications',
                                            blank=True,
                                            verbose_name=_('Preferred Roles'))
    preferred_tasks = models.TextField(_('Preferred Tasks'), blank=True)

    # Contact
    emergency_contact_name = models.CharField(_('Emergency Contact Name'),
                                             max_length=200)
    emergency_contact_phone = models.CharField(_('Emergency Contact Phone'),
                                              max_length=20)

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='pending')
    reviewed_at = models.DateTimeField(_('Reviewed At'), null=True, blank=True)
    reviewed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='reviewed_applications',
                                   verbose_name=_('Reviewed By'))
    review_notes = models.TextField(_('Review Notes'), blank=True)

    class Meta:
        verbose_name = _('Volunteer Application')
        verbose_name_plural = _('Volunteer Applications')
        db_table = 'volunteer_applications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.get_status_display()}'


class TrainingModule(TimeStampedUUIDModel):
    """Training modules for volunteers"""

    MODULE_TYPE_CHOICES = [
        ('onboarding', 'Onboarding'),
        ('role_specific', 'Role-Specific'),
        ('safety', 'Safety & Security'),
        ('customer_service', 'Customer Service'),
        ('technical', 'Technical Skills'),
    ]

    title = models.CharField(_('Module Title'), max_length=200)
    description = models.TextField(_('Description'))
    module_type = models.CharField(_('Module Type'), max_length=20,
                                   choices=MODULE_TYPE_CHOICES)

    # Content
    content = models.TextField(_('Module Content'),
                              help_text='Training material, can include markdown')
    video_url = models.URLField(_('Video URL'), blank=True)
    attachments = models.JSONField(_('Attachments'), default=list,
                                  help_text='List of attachment URLs')

    # Requirements
    is_required = models.BooleanField(_('Is Required'), default=True)
    required_for_roles = models.ManyToManyField('volunteers.VolunteerRole',
                                               related_name='required_training',
                                               blank=True,
                                               verbose_name=_('Required For Roles'))
    prerequisite_modules = models.ManyToManyField('self', symmetrical=False,
                                                  blank=True,
                                                  verbose_name=_('Prerequisite Modules'))

    # Settings
    estimated_duration_minutes = models.PositiveIntegerField(_('Estimated Duration (minutes)'),
                                                            default=30)
    passing_score = models.PositiveIntegerField(_('Passing Score %'), default=70,
                                               help_text='Minimum score to pass quiz')

    # Quiz questions
    quiz_questions = models.JSONField(_('Quiz Questions'), default=list,
                                     help_text='List of quiz questions with answers')

    # Status
    is_active = models.BooleanField(_('Is Active'), default=True)
    display_order = models.PositiveIntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Training Module')
        verbose_name_plural = _('Training Modules')
        db_table = 'training_modules'
        ordering = ['display_order', 'title']

    def __str__(self):
        return self.title


class VolunteerTrainingProgress(TimeStampedUUIDModel):
    """Track volunteer training progress"""

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    volunteer = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='training_progress',
                                 verbose_name=_('Volunteer'))
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE,
                              related_name='progress_records',
                              verbose_name=_('Module'))

    # Progress
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='not_started')
    progress_percentage = models.PositiveIntegerField(_('Progress %'), default=0)

    # Completion
    started_at = models.DateTimeField(_('Started At'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(_('Time Spent (minutes)'), default=0)

    # Quiz results
    quiz_score = models.PositiveIntegerField(_('Quiz Score %'), null=True, blank=True)
    quiz_attempts = models.PositiveIntegerField(_('Quiz Attempts'), default=0)
    passed_quiz = models.BooleanField(_('Passed Quiz'), default=False)

    class Meta:
        verbose_name = _('Training Progress')
        verbose_name_plural = _('Training Progress')
        db_table = 'volunteer_training_progress'
        unique_together = [['volunteer', 'module']]
        ordering = ['volunteer', 'module']

    def __str__(self):
        return f'{self.volunteer.email} - {self.module.title} ({self.status})'


class VolunteerHours(TimeStampedUUIDModel):
    """Track volunteer hours"""

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    volunteer = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='volunteer_hours',
                                 verbose_name=_('Volunteer'))
    shift = models.ForeignKey('volunteers.VolunteerShift', on_delete=models.CASCADE,
                             null=True, blank=True,
                             related_name='hour_logs',
                             verbose_name=_('Shift'))

    # Time tracking
    date = models.DateField(_('Date'))
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    hours = models.DecimalField(_('Hours'), max_digits=5, decimal_places=2)

    # Activity
    activity_description = models.TextField(_('Activity Description'))
    role = models.ForeignKey('volunteers.VolunteerRole', on_delete=models.SET_NULL,
                            null=True, blank=True,
                            verbose_name=_('Role'))

    # Approval
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='pending')
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='approved_hours',
                                   verbose_name=_('Approved By'))
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Volunteer Hours')
        verbose_name_plural = _('Volunteer Hours')
        db_table = 'volunteer_hours'
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f'{self.volunteer.email} - {self.date} ({self.hours}h)'

    def save(self, *args, **kwargs):
        # Calculate hours if not set
        if not self.hours and self.start_time and self.end_time:
            from datetime import datetime, timedelta
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            if end < start:
                end += timedelta(days=1)  # Handle overnight shifts
            duration = end - start
            self.hours = duration.total_seconds() / 3600
        super().save(*args, **kwargs)


class VolunteerRecognition(TimeStampedUUIDModel):
    """Recognition and rewards for volunteers"""

    RECOGNITION_TYPE_CHOICES = [
        ('badge', 'Badge'),
        ('certificate', 'Certificate'),
        ('award', 'Award'),
        ('shoutout', 'Public Shoutout'),
        ('gift', 'Gift/Reward'),
    ]

    volunteer = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='recognitions',
                                 verbose_name=_('Volunteer'))

    # Recognition details
    recognition_type = models.CharField(_('Recognition Type'), max_length=20,
                                       choices=RECOGNITION_TYPE_CHOICES)
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))

    # Badge/Award details
    icon = models.ImageField(_('Icon/Badge Image'), upload_to='volunteer_badges/',
                            null=True, blank=True)
    color = models.CharField(_('Color'), max_length=7, default='#FFD700')

    # Criteria
    hours_threshold = models.PositiveIntegerField(_('Hours Threshold'), null=True, blank=True,
                                                 help_text='Minimum hours to earn this')
    events_threshold = models.PositiveIntegerField(_('Events Threshold'), null=True, blank=True,
                                                  help_text='Minimum events to earn this')

    # Status
    awarded_at = models.DateTimeField(_('Awarded At'))
    awarded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='awarded_recognitions',
                                  verbose_name=_('Awarded By'))

    # Display
    is_public = models.BooleanField(_('Is Public'), default=True)
    display_on_profile = models.BooleanField(_('Display on Profile'), default=True)

    class Meta:
        verbose_name = _('Volunteer Recognition')
        verbose_name_plural = _('Volunteer Recognitions')
        db_table = 'volunteer_recognitions'
        ordering = ['-awarded_at']

    def __str__(self):
        return f'{self.volunteer.email} - {self.title}'


class VolunteerLeaderboard(TimeStampedUUIDModel):
    """Leaderboard for volunteers"""

    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time'),
    ]

    period = models.CharField(_('Period'), max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField(_('Period Start'))
    period_end = models.DateField(_('Period End'))

    # Rankings (stored as JSON for performance)
    rankings = models.JSONField(_('Rankings'), default=list,
                               help_text='List of volunteer rankings with stats')

    # Metadata
    last_updated = models.DateTimeField(_('Last Updated'), auto_now=True)
    total_participants = models.PositiveIntegerField(_('Total Participants'), default=0)

    class Meta:
        verbose_name = _('Volunteer Leaderboard')
        verbose_name_plural = _('Volunteer Leaderboards')
        db_table = 'volunteer_leaderboards'
        unique_together = [['period', 'period_start']]
        ordering = ['-period_start']

    def __str__(self):
        return f'{self.get_period_display()} - {self.period_start}'

    def calculate_rankings(self):
        """Calculate volunteer rankings for this period"""
        from django.db.models import Sum, Count

        # Get volunteers active in this period
        volunteer_stats = VolunteerHours.objects.filter(
            date__gte=self.period_start,
            date__lte=self.period_end,
            status='approved'
        ).values('volunteer').annotate(
            total_hours=Sum('hours'),
            total_shifts=Count('shift', distinct=True)
        ).order_by('-total_hours')

        rankings = []
        for rank, stats in enumerate(volunteer_stats, start=1):
            from nexus.users.models import User
            volunteer = User.objects.get(id=stats['volunteer'])

            rankings.append({
                'rank': rank,
                'volunteer_id': str(volunteer.id),
                'volunteer_name': volunteer.get_full_name(),
                'volunteer_email': volunteer.email,
                'total_hours': float(stats['total_hours']),
                'total_shifts': stats['total_shifts']
            })

        self.rankings = rankings
        self.total_participants = len(rankings)
        self.save()

        return rankings
