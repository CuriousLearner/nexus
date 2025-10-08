# Third Party Stuff
from django.contrib import admin

# Nexus Stuff
from nexus.volunteers.models import (
    VolunteerAssignment,
    VolunteerHours,
    VolunteerRole,
    VolunteerShift,
    VolunteerTask,
)


@admin.register(VolunteerRole)
class VolunteerRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'volunteers_needed', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'required_skills')


@admin.register(VolunteerShift)
class VolunteerShiftAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'role', 'start_time', 'end_time', 'status', 'current_volunteers_count', 'max_volunteers')
    list_filter = ('event', 'role', 'status', 'start_time')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_time'

    def current_volunteers_count(self, obj):
        return obj.current_volunteers_count()
    current_volunteers_count.short_description = 'Current Volunteers'


@admin.register(VolunteerAssignment)
class VolunteerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'shift', 'status', 'assigned_at', 'checked_in_at', 'rating')
    list_filter = ('status', 'shift__event', 'assigned_at')
    search_fields = ('volunteer__email', 'volunteer__first_name', 'volunteer__last_name', 'shift__title')
    readonly_fields = ('assigned_at',)
    date_hierarchy = 'assigned_at'


@admin.register(VolunteerTask)
class VolunteerTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'assigned_to', 'status', 'priority', 'due_date')
    list_filter = ('event', 'status', 'priority', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__email')
    date_hierarchy = 'due_date'


@admin.register(VolunteerHours)
class VolunteerHoursAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'event', 'total_hours', 'last_updated')
    list_filter = ('event', 'last_updated')
    search_fields = ('volunteer__email', 'volunteer__first_name', 'volunteer__last_name')
    readonly_fields = ('total_hours', 'last_updated')
    actions = ['recalculate_hours']

    def recalculate_hours(self, request, queryset):
        for volunteer_hours in queryset:
            volunteer_hours.recalculate_hours()
        self.message_user(request, f'{queryset.count()} volunteer hours recalculated successfully.')
    recalculate_hours.short_description = 'Recalculate selected volunteer hours'
