# Generated migration file

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('proposals', '0003_add_scoring_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Event Name')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Description')),
                ('tagline', models.CharField(blank=True, max_length=300, verbose_name='Tagline')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(verbose_name='End Date')),
                ('registration_start', models.DateTimeField(verbose_name='Registration Start')),
                ('registration_end', models.DateTimeField(verbose_name='Registration End')),
                ('cfp_start', models.DateTimeField(blank=True, null=True, verbose_name='CFP Start')),
                ('cfp_end', models.DateTimeField(blank=True, null=True, verbose_name='CFP End')),
                ('venue_name', models.CharField(blank=True, max_length=200, verbose_name='Venue Name')),
                ('venue_address', models.TextField(blank=True, verbose_name='Venue Address')),
                ('city', models.CharField(max_length=100, verbose_name='City')),
                ('country', models.CharField(max_length=100, verbose_name='Country')),
                ('is_virtual', models.BooleanField(default=False, verbose_name='Is Virtual')),
                ('virtual_platform', models.CharField(blank=True, help_text='e.g., Zoom, Google Meet', max_length=100, verbose_name='Virtual Platform')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('ongoing', 'Ongoing'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='draft', max_length=20, verbose_name='Status')),
                ('max_attendees', models.PositiveIntegerField(blank=True, null=True, verbose_name='Max Attendees')),
                ('website_url', models.URLField(blank=True, verbose_name='Website URL')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='event_logos/', verbose_name='Logo')),
                ('banner', models.ImageField(blank=True, null=True, upload_to='event_banners/', verbose_name='Banner')),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
                'db_table': 'events',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Venue Name')),
                ('capacity', models.PositiveIntegerField(verbose_name='Capacity')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('floor', models.CharField(blank=True, max_length=50, verbose_name='Floor')),
                ('has_projector', models.BooleanField(default=True, verbose_name='Has Projector')),
                ('has_microphone', models.BooleanField(default=True, verbose_name='Has Microphone')),
                ('has_whiteboard', models.BooleanField(default=False, verbose_name='Has Whiteboard')),
                ('additional_equipment', models.TextField(blank=True, verbose_name='Additional Equipment')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='venues', to='events.event', verbose_name='Event')),
            ],
            options={
                'verbose_name': 'Venue',
                'verbose_name_plural': 'Venues',
                'db_table': 'event_venues',
                'ordering': ['event', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('session_type', models.CharField(choices=[('talk', 'Talk'), ('workshop', 'Workshop'), ('panel', 'Panel Discussion'), ('keynote', 'Keynote'), ('lightning', 'Lightning Talk'), ('break', 'Break'), ('social', 'Social Event')], default='talk', max_length=20, verbose_name='Session Type')),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('end_time', models.DateTimeField(verbose_name='End Time')),
                ('is_recorded', models.BooleanField(default=True, verbose_name='Is Recorded')),
                ('recording_url', models.URLField(blank=True, verbose_name='Recording URL')),
                ('slides_url', models.URLField(blank=True, verbose_name='Slides URL')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='events.event', verbose_name='Event')),
                ('proposal', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session', to='proposals.proposal', verbose_name='Proposal')),
                ('speakers', models.ManyToManyField(related_name='sessions', to=settings.AUTH_USER_MODEL, verbose_name='Speakers')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sessions', to='events.venue', verbose_name='Venue')),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'db_table': 'event_sessions',
                'ordering': ['event', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Sponsor Name')),
                ('tier', models.CharField(choices=[('platinum', 'Platinum'), ('gold', 'Gold'), ('silver', 'Silver'), ('bronze', 'Bronze'), ('community', 'Community')], max_length=20, verbose_name='Tier')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='sponsor_logos/', verbose_name='Logo')),
                ('website_url', models.URLField(blank=True, verbose_name='Website URL')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('contact_name', models.CharField(blank=True, max_length=200, verbose_name='Contact Name')),
                ('contact_email', models.EmailField(blank=True, max_length=254, verbose_name='Contact Email')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='Display Order')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sponsors', to='events.event', verbose_name='Event')),
            ],
            options={
                'verbose_name': 'Sponsor',
                'verbose_name_plural': 'Sponsors',
                'db_table': 'event_sponsors',
                'ordering': ['event', 'tier', 'display_order'],
            },
        ),
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('registered', 'Registered'), ('confirmed', 'Confirmed'), ('checked_in', 'Checked In'), ('cancelled', 'Cancelled'), ('no_show', 'No Show')], default='registered', max_length=20, verbose_name='Status')),
                ('registration_date', models.DateTimeField(auto_now_add=True, verbose_name='Registration Date')),
                ('checked_in_at', models.DateTimeField(blank=True, null=True, verbose_name='Checked In At')),
                ('ticket_number', models.CharField(max_length=50, unique=True, verbose_name='Ticket Number')),
                ('ticket_type', models.CharField(blank=True, help_text='e.g., Early Bird, Regular, VIP', max_length=100, verbose_name='Ticket Type')),
                ('dietary_requirements', models.TextField(blank=True, verbose_name='Dietary Requirements')),
                ('accessibility_requirements', models.TextField(blank=True, verbose_name='Accessibility Requirements')),
                ('special_requests', models.TextField(blank=True, verbose_name='Special Requests')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendees', to='events.event', verbose_name='Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_attendances', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Attendee',
                'verbose_name_plural': 'Attendees',
                'db_table': 'event_attendees',
                'ordering': ['-registration_date'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='attendee',
            unique_together={('event', 'user')},
        ),
    ]
