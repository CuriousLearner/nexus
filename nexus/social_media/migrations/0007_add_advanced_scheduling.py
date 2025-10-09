# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social_media', '0006_add_platform_schedules_and_video'),
    ]

    operations = [
        # Recurring posts
        migrations.CreateModel(
            name='RecurringPost',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('text', models.TextField(verbose_name='Content Text')),
                ('image', models.ImageField(blank=True, null=True, upload_to='recurring_posts/', verbose_name='Image')),
                ('video', models.FileField(blank=True, null=True, upload_to='recurring_posts_videos/', verbose_name='Video')),
                ('posted_at', models.CharField(blank=True, choices=[('fb', 'Facebook'), ('twitter', 'Twitter'), ('linkedin', 'Linkedin'), ('instagram', 'Instagram'), ('threads', 'Threads')], max_length=10, null=True, verbose_name='Posted at platform')),
                ('platforms', models.JSONField(blank=True, default=list, help_text='List of platforms for multi-platform posting', verbose_name='Platforms')),
                ('frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('biweekly', 'Bi-weekly'), ('monthly', 'Monthly'), ('custom', 'Custom')], max_length=20, verbose_name='Frequency')),
                ('start_date', models.DateTimeField(verbose_name='Start Date')),
                ('end_date', models.DateTimeField(blank=True, help_text='Leave empty for indefinite', null=True, verbose_name='End Date')),
                ('time_of_day', models.TimeField(help_text='What time to post each day', verbose_name='Time of Day')),
                ('weekdays', models.JSONField(blank=True, default=list, help_text='List of weekday numbers (0=Monday, 6=Sunday) for weekly posts', verbose_name='Weekdays')),
                ('day_of_month', models.PositiveIntegerField(blank=True, help_text='Day of month (1-31) for monthly posts', null=True, verbose_name='Day of Month')),
                ('custom_interval_days', models.PositiveIntegerField(blank=True, help_text='Interval in days for custom frequency', null=True, verbose_name='Custom Interval (days)')),
                ('status', models.CharField(choices=[('active', 'Active'), ('paused', 'Paused'), ('completed', 'Completed')], default='active', max_length=20, verbose_name='Status')),
                ('last_posted_at', models.DateTimeField(blank=True, null=True, verbose_name='Last Posted At')),
                ('next_post_at', models.DateTimeField(blank=True, null=True, verbose_name='Next Post At')),
                ('total_posts_created', models.PositiveIntegerField(default=0, verbose_name='Total Posts Created')),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Posted by')),
            ],
            options={
                'verbose_name': 'Recurring Post',
                'verbose_name_plural': 'Recurring Posts',
                'db_table': 'recurring_posts',
                'ordering': ['-created_at'],
            },
        ),

        # Post templates
        migrations.CreateModel(
            name='PostTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Template Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('text_template', models.TextField(help_text='Use {{variable_name}} for placeholders', verbose_name='Text Template')),
                ('image', models.ImageField(blank=True, null=True, upload_to='post_templates/', verbose_name='Default Image')),
                ('video', models.FileField(blank=True, null=True, upload_to='post_template_videos/', verbose_name='Default Video')),
                ('default_platforms', models.JSONField(blank=True, default=list, help_text='Default platforms to post to', verbose_name='Default Platforms')),
                ('times_used', models.PositiveIntegerField(default=0, verbose_name='Times Used')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='Last Used At')),
                ('category', models.CharField(blank=True, help_text='e.g., Announcement, Promotion, Update', max_length=100, verbose_name='Category')),
                ('tags', models.JSONField(blank=True, default=list, verbose_name='Tags')),
                ('is_public', models.BooleanField(default=False, help_text='Allow other users to use this template', verbose_name='Is Public')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_templates', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
            ],
            options={
                'verbose_name': 'Post Template',
                'verbose_name_plural': 'Post Templates',
                'db_table': 'post_templates',
                'ordering': ['-created_at'],
            },
        ),

        migrations.CreateModel(
            name='TemplateVariable',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Variable name without curly braces', max_length=100, verbose_name='Variable Name')),
                ('description', models.TextField(blank=True, help_text='What this variable represents', verbose_name='Description')),
                ('default_value', models.TextField(blank=True, verbose_name='Default Value')),
                ('is_required', models.BooleanField(default=False, verbose_name='Is Required')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variables', to='social_media.posttemplate', verbose_name='Template')),
            ],
            options={
                'verbose_name': 'Template Variable',
                'verbose_name_plural': 'Template Variables',
                'db_table': 'template_variables',
                'ordering': ['template', 'name'],
            },
        ),

        migrations.AlterUniqueTogether(
            name='templatevariable',
            unique_together={('template', 'name')},
        ),

        # Post queue
        migrations.CreateModel(
            name='PostQueue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('queue_position', models.PositiveIntegerField(default=0, help_text='Lower number = higher priority', verbose_name='Queue Position')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')], default='normal', max_length=20, verbose_name='Priority')),
                ('auto_schedule', models.BooleanField(default=False, help_text='Automatically schedule when slot available', verbose_name='Auto Schedule')),
                ('preferred_time_start', models.TimeField(blank=True, null=True, verbose_name='Preferred Time Start')),
                ('preferred_time_end', models.TimeField(blank=True, null=True, verbose_name='Preferred Time End')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='queue_item', to='social_media.post', verbose_name='Post')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_queue_items', to=settings.AUTH_USER_MODEL, verbose_name='Assigned To')),
            ],
            options={
                'verbose_name': 'Post Queue Item',
                'verbose_name_plural': 'Post Queue Items',
                'db_table': 'post_queue',
                'ordering': ['queue_position', '-priority', 'created_at'],
            },
        ),

        migrations.CreateModel(
            name='SchedulingRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, verbose_name='Rule Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('weekdays', models.JSONField(default=list, help_text='List of weekday numbers (0=Monday, 6=Sunday)', verbose_name='Weekdays')),
                ('time_slots', models.JSONField(default=list, help_text='List of time ranges like [["09:00", "10:00"], ["14:00", "15:00"]]', verbose_name='Time Slots')),
                ('max_posts_per_day', models.PositiveIntegerField(default=5, verbose_name='Max Posts Per Day')),
                ('min_hours_between_posts', models.PositiveIntegerField(default=2, verbose_name='Min Hours Between Posts')),
                ('platforms', models.JSONField(blank=True, default=list, help_text='Apply rule to specific platforms only', verbose_name='Platforms')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
            ],
            options={
                'verbose_name': 'Scheduling Rule',
                'verbose_name_plural': 'Scheduling Rules',
                'db_table': 'scheduling_rules',
                'ordering': ['name'],
            },
        ),
    ]
