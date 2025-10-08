# Third Party Stuff
from django.contrib import admin

# Nexus Stuff
from nexus.events.models import Attendee, Event, Session, Sponsor, Venue


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'city', 'status', 'is_virtual')
    list_filter = ('status', 'is_virtual', 'start_date')
    search_fields = ('name', 'city', 'country', 'description')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'start_date'


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'capacity', 'floor', 'has_projector', 'has_microphone')
    list_filter = ('event', 'has_projector', 'has_microphone', 'has_whiteboard')
    search_fields = ('name', 'description')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'venue', 'session_type', 'start_time', 'end_time')
    list_filter = ('event', 'session_type', 'is_recorded', 'start_time')
    search_fields = ('title', 'description')
    filter_horizontal = ('speakers',)
    date_hierarchy = 'start_time'


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'ticket_number', 'registration_date', 'checked_in_at')
    list_filter = ('event', 'status', 'registration_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ticket_number')
    readonly_fields = ('registration_date', 'ticket_number')
    date_hierarchy = 'registration_date'


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'tier', 'display_order')
    list_filter = ('event', 'tier')
    search_fields = ('name', 'description')
    list_editable = ('display_order',)
