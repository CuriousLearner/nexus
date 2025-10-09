# Generated migration file

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0005_add_multi_platform_support'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='posted_at',
            field=models.CharField(
                blank=True,
                choices=[('fb', 'Facebook'), ('twitter', 'Twitter'), ('linkedin', 'Linkedin'), ('instagram', 'Instagram'), ('threads', 'Threads')],
                help_text='Leave empty for multi-platform posting',
                max_length=10,
                null=True,
                verbose_name='Posted at platform'
            ),
        ),
        migrations.AddField(
            model_name='post',
            name='video',
            field=models.FileField(blank=True, help_text='Video file for the post', null=True, upload_to='post_videos/', verbose_name='Video'),
        ),
        migrations.AddField(
            model_name='post',
            name='use_platform_schedules',
            field=models.BooleanField(default=False, help_text='Use individual platform schedules instead of single scheduled_time', verbose_name='Use Platform Schedules'),
        ),
        migrations.CreateModel(
            name='PlatformSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('platform', models.CharField(choices=[('fb', 'Facebook'), ('twitter', 'Twitter'), ('linkedin', 'Linkedin'), ('instagram', 'Instagram'), ('threads', 'Threads')], max_length=20, verbose_name='Platform')),
                ('scheduled_time', models.DateTimeField(verbose_name='Scheduled Time')),
                ('is_posted', models.BooleanField(default=False, verbose_name='Is Posted')),
                ('posted_time', models.DateTimeField(blank=True, null=True, verbose_name='Posted Time')),
                ('error_message', models.TextField(blank=True, help_text='Error if posting failed', verbose_name='Error Message')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='platform_schedules', to='social_media.post', verbose_name='Post')),
            ],
            options={
                'verbose_name': 'Platform Schedule',
                'verbose_name_plural': 'Platform Schedules',
                'db_table': 'platform_schedules',
                'ordering': ['scheduled_time'],
            },
        ),
        migrations.AddIndex(
            model_name='platformschedule',
            index=models.Index(fields=['scheduled_time', 'is_posted'], name='platform_sc_schedul_idx'),
        ),
        migrations.AddIndex(
            model_name='platformschedule',
            index=models.Index(fields=['platform', 'is_posted'], name='platform_sc_platfor_idx'),
        ),
    ]
