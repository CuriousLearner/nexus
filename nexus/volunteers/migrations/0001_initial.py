# Generated migration file

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VolunteerRole',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Role Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('required_skills', models.TextField(blank=True, verbose_name='Required Skills')),
                ('volunteers_needed', models.PositiveIntegerField(default=1, verbose_name='Volunteers Needed')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
            ],
            options={
                'verbose_name': 'Volunteer Role',
                'verbose_name_plural': 'Volunteer Roles',
                'db_table': 'volunteer_roles',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='VolunteerShift',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200, verbose_name='Shift Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('end_time', models.DateTimeField(verbose_name='End Time')),
                ('max_volunteers', models.PositiveIntegerField(default=1, verbose_name='Max Volunteers')),
                ('status', models.CharField(choices=[('open', 'Open'), ('full', 'Full'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='open', max_length=20, verbose_name='Status')),
                ('location', models.CharField(blank=True, max_length=200, verbose_name='Location')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_shifts', to='events.event', verbose_name='Event')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shifts', to='volunteers.volunteerrole', verbose_name='Role')),
            ],
            options={
                'verbose_name': 'Volunteer Shift',
                'verbose_name_plural': 'Volunteer Shifts',
                'db_table': 'volunteer_shifts',
                'ordering': ['event', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='VolunteerAssignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('checked_in', 'Checked In'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('no_show', 'No Show')], default='pending', max_length=20, verbose_name='Status')),
                ('assigned_at', models.DateTimeField(auto_now_add=True, verbose_name='Assigned At')),
                ('confirmed_at', models.DateTimeField(blank=True, null=True, verbose_name='Confirmed At')),
                ('checked_in_at', models.DateTimeField(blank=True, null=True, verbose_name='Checked In At')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Completed At')),
                ('notes', models.TextField(blank=True, help_text='Notes from volunteer or coordinator', verbose_name='Notes')),
                ('rating', models.PositiveIntegerField(blank=True, help_text='Rating from 1-5', null=True, verbose_name='Rating')),
                ('feedback', models.TextField(blank=True, verbose_name='Feedback')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='volunteers.volunteershift', verbose_name='Shift')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_assignments', to=settings.AUTH_USER_MODEL, verbose_name='Volunteer')),
            ],
            options={
                'verbose_name': 'Volunteer Assignment',
                'verbose_name_plural': 'Volunteer Assignments',
                'db_table': 'volunteer_assignments',
                'ordering': ['-assigned_at'],
            },
        ),
        migrations.CreateModel(
            name='VolunteerTask',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200, verbose_name='Task Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('status', models.CharField(choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='todo', max_length=20, verbose_name='Status')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20, verbose_name='Priority')),
                ('due_date', models.DateTimeField(blank=True, null=True, verbose_name='Due Date')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Completed At')),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Assigned By')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Assigned To')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_tasks', to='events.event', verbose_name='Event')),
            ],
            options={
                'verbose_name': 'Volunteer Task',
                'verbose_name_plural': 'Volunteer Tasks',
                'db_table': 'volunteer_tasks',
                'ordering': ['-priority', 'due_date'],
            },
        ),
        migrations.CreateModel(
            name='VolunteerHours',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('total_hours', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Total Hours')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_hours_records', to='events.event', verbose_name='Event')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_hours', to=settings.AUTH_USER_MODEL, verbose_name='Volunteer')),
            ],
            options={
                'verbose_name': 'Volunteer Hours',
                'verbose_name_plural': 'Volunteer Hours',
                'db_table': 'volunteer_hours',
                'ordering': ['-total_hours'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='volunteerassignment',
            unique_together={('shift', 'volunteer')},
        ),
        migrations.AlterUniqueTogether(
            name='volunteerhours',
            unique_together={('volunteer', 'event')},
        ),
    ]
