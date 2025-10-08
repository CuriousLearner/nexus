# Generated migration file

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0002_add_draft_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostAnalytics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('likes', models.PositiveIntegerField(default=0, verbose_name='Likes')),
                ('shares', models.PositiveIntegerField(default=0, verbose_name='Shares')),
                ('comments', models.PositiveIntegerField(default=0, verbose_name='Comments')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='Views')),
                ('clicks', models.PositiveIntegerField(default=0, verbose_name='Clicks')),
                ('reach', models.PositiveIntegerField(default=0, help_text='Number of unique users who saw the post', verbose_name='Reach')),
                ('engagement_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Percentage of engagement', max_digits=5, verbose_name='Engagement Rate')),
                ('last_synced_at', models.DateTimeField(blank=True, help_text='Last time analytics were synced from platform', null=True, verbose_name='Last Synced At')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='social_media.post', verbose_name='Post')),
            ],
            options={
                'verbose_name': 'Post Analytics',
                'verbose_name_plural': 'Post Analytics',
                'db_table': 'post_analytics',
            },
        ),
    ]
