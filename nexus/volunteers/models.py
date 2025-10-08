# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _
from extended_choices import Choices

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class VolunteerRole(TimeStampedUUIDModel):
    """Model to define volunteer roles"""

    name = models.CharField(_('Role Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    required_skills = models.TextField(_('Required Skills'), blank=True)
    volunteers_needed = models.PositiveIntegerField(_('Volunteers Needed'), default=1)
    is_active = models.BooleanField(_('Is Active'), default=True)

    class Meta:
        verbose_name = _('Volunteer Role')
        verbose_name_plural = _('Volunteer Roles')
        db_table = 'volunteer_roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class VolunteerShift(TimeStampedUUIDModel):
    """Model to manage volunteer shifts"""

    STATUS_CHOICES = Choices(
        ('OPEN', 'open', _('Open')),
        ('FULL', 'full', _('Full')),
        ('IN_PROGRESS', 'in_progress', _('In Progress')),
        ('COMPLETED', 'completed', _('Completed')),
        ('CANCELLED', 'cancelled', _('Cancelled')),
    )

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             related_name='volunteer_shifts', verbose_name=_('Event'))
    role = models.ForeignKey(VolunteerRole, on_delete=models.PROTECT,
                            related_name='shifts', verbose_name=_('Role'))

    title = models.CharField(_('Shift Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    # Timing
    start_time = models.DateTimeField(_('Start Time'))
    end_time = models.DateTimeField(_('End Time'))

    # Capacity
    max_volunteers = models.PositiveIntegerField(_('Max Volunteers'), default=1)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default=STATUS_CHOICES.OPEN)

    # Location
    location = models.CharField(_('Location'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('Volunteer Shift')
        verbose_name_plural = _('Volunteer Shifts')
        db_table = 'volunteer_shifts'
        ordering = ['event', 'start_time']

    def __str__(self):
        return f'{self.event.name} - {self.title} ({self.start_time})'

    def current_volunteers_count(self):
        """Get current number of volunteers assigned"""
        return self.assignments.filter(status=VolunteerAssignment.STATUS_CHOICES.CONFIRMED).count()

    def is_full(self):
        """Check if shift is full"""
        return self.current_volunteers_count() >= self.max_volunteers


class VolunteerAssignment(TimeStampedUUIDModel):
    """Model to assign volunteers to shifts"""

    STATUS_CHOICES = Choices(
        ('PENDING', 'pending', _('Pending')),
        ('CONFIRMED', 'confirmed', _('Confirmed')),
        ('CHECKED_IN', 'checked_in', _('Checked In')),
        ('COMPLETED', 'completed', _('Completed')),
        ('CANCELLED', 'cancelled', _('Cancelled')),
        ('NO_SHOW', 'no_show', _('No Show')),
    )

    shift = models.ForeignKey(VolunteerShift, on_delete=models.CASCADE,
                             related_name='assignments', verbose_name=_('Shift'))
    volunteer = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='volunteer_assignments', verbose_name=_('Volunteer'))

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default=STATUS_CHOICES.PENDING)
    assigned_at = models.DateTimeField(_('Assigned At'), auto_now_add=True)
    confirmed_at = models.DateTimeField(_('Confirmed At'), null=True, blank=True)
    checked_in_at = models.DateTimeField(_('Checked In At'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)

    # Feedback
    notes = models.TextField(_('Notes'), blank=True,
                            help_text='Notes from volunteer or coordinator')
    rating = models.PositiveIntegerField(_('Rating'), null=True, blank=True,
                                        help_text='Rating from 1-5')
    feedback = models.TextField(_('Feedback'), blank=True)

    class Meta:
        verbose_name = _('Volunteer Assignment')
        verbose_name_plural = _('Volunteer Assignments')
        db_table = 'volunteer_assignments'
        unique_together = [['shift', 'volunteer']]
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.volunteer.email} - {self.shift.title}'

    def hours_worked(self):
        """Calculate hours worked"""
        if self.shift.start_time and self.shift.end_time:
            delta = self.shift.end_time - self.shift.start_time
            return delta.total_seconds() / 3600
        return 0


class VolunteerTask(TimeStampedUUIDModel):
    """Model to manage specific volunteer tasks"""

    STATUS_CHOICES = Choices(
        ('TODO', 'todo', _('To Do')),
        ('IN_PROGRESS', 'in_progress', _('In Progress')),
        ('COMPLETED', 'completed', _('Completed')),
        ('CANCELLED', 'cancelled', _('Cancelled')),
    )

    PRIORITY_CHOICES = Choices(
        ('LOW', 'low', _('Low')),
        ('MEDIUM', 'medium', _('Medium')),
        ('HIGH', 'high', _('High')),
        ('URGENT', 'urgent', _('Urgent')),
    )

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             related_name='volunteer_tasks', verbose_name=_('Event'))
    title = models.CharField(_('Task Title'), max_length=200)
    description = models.TextField(_('Description'))
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='assigned_tasks',
                                   verbose_name=_('Assigned To'))
    assigned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                   related_name='created_tasks', verbose_name=_('Assigned By'))

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default=STATUS_CHOICES.TODO)
    priority = models.CharField(_('Priority'), max_length=20, choices=PRIORITY_CHOICES,
                               default=PRIORITY_CHOICES.MEDIUM)

    due_date = models.DateTimeField(_('Due Date'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Volunteer Task')
        verbose_name_plural = _('Volunteer Tasks')
        db_table = 'volunteer_tasks'
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return f'{self.event.name} - {self.title}'


class VolunteerHours(TimeStampedUUIDModel):
    """Model to track total volunteer hours"""

    volunteer = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='volunteer_hours', verbose_name=_('Volunteer'))
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,
                             related_name='volunteer_hours_records', verbose_name=_('Event'))

    total_hours = models.DecimalField(_('Total Hours'), max_digits=6, decimal_places=2, default=0)
    last_updated = models.DateTimeField(_('Last Updated'), auto_now=True)

    class Meta:
        verbose_name = _('Volunteer Hours')
        verbose_name_plural = _('Volunteer Hours')
        db_table = 'volunteer_hours'
        unique_together = [['volunteer', 'event']]
        ordering = ['-total_hours']

    def __str__(self):
        return f'{self.volunteer.email} - {self.event.name}: {self.total_hours}h'

    def recalculate_hours(self):
        """Recalculate total hours from completed assignments"""
        total = sum(
            assignment.hours_worked()
            for assignment in self.volunteer.volunteer_assignments.filter(
                shift__event=self.event,
                status=VolunteerAssignment.STATUS_CHOICES.COMPLETED
            )
        )
        self.total_hours = total
        self.save()
