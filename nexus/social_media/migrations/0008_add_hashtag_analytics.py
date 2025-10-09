# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0007_add_advanced_scheduling'),
    ]

    operations = [
        # Hashtag model
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('tag', models.CharField(db_index=True, help_text='Hashtag without the # symbol', max_length=100, unique=True, verbose_name='Tag')),
                ('tag_lower', models.CharField(db_index=True, max_length=100, verbose_name='Tag (lowercase)')),
                ('total_uses', models.PositiveIntegerField(default=0, verbose_name='Total Uses')),
                ('total_posts', models.PositiveIntegerField(default=0, verbose_name='Total Posts')),
                ('first_used_at', models.DateTimeField(auto_now_add=True, verbose_name='First Used At')),
                ('last_used_at', models.DateTimeField(auto_now=True, verbose_name='Last Used At')),
                ('total_impressions', models.BigIntegerField(default=0, verbose_name='Total Impressions')),
                ('total_engagements', models.BigIntegerField(default=0, verbose_name='Total Engagements')),
                ('total_clicks', models.BigIntegerField(default=0, verbose_name='Total Clicks')),
                ('category', models.CharField(blank=True, help_text='e.g., Technology, Marketing, Events', max_length=50, verbose_name='Category')),
                ('is_trending', models.BooleanField(default=False, verbose_name='Is Trending')),
                ('is_banned', models.BooleanField(default=False, help_text='Flag inappropriate hashtags', verbose_name='Is Banned')),
            ],
            options={
                'verbose_name': 'Hashtag',
                'verbose_name_plural': 'Hashtags',
                'db_table': 'hashtags',
                'ordering': ['-total_uses', '-last_used_at'],
            },
        ),

        # Add indexes for Hashtag
        migrations.AddIndex(
            model_name='hashtag',
            index=models.Index(fields=['-total_uses'], name='hashtags_total_u_idx'),
        ),
        migrations.AddIndex(
            model_name='hashtag',
            index=models.Index(fields=['-last_used_at'], name='hashtags_last_us_idx'),
        ),

        # PostHashtag model
        migrations.CreateModel(
            name='PostHashtag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('platform', models.CharField(blank=True, choices=[('fb', 'Facebook'), ('twitter', 'Twitter'), ('linkedin', 'Linkedin'), ('instagram', 'Instagram'), ('threads', 'Threads')], max_length=20, verbose_name='Platform')),
                ('impressions', models.BigIntegerField(default=0, verbose_name='Impressions')),
                ('engagements', models.BigIntegerField(default=0, help_text='Likes, shares, comments', verbose_name='Engagements')),
                ('clicks', models.BigIntegerField(default=0, verbose_name='Clicks')),
                ('reach', models.BigIntegerField(default=0, verbose_name='Reach')),
                ('hashtag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_hashtags', to='social_media.hashtag', verbose_name='Hashtag')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_hashtags', to='social_media.post', verbose_name='Post')),
            ],
            options={
                'verbose_name': 'Post Hashtag',
                'verbose_name_plural': 'Post Hashtags',
                'db_table': 'post_hashtags',
                'ordering': ['-created_at'],
            },
        ),

        migrations.AlterUniqueTogether(
            name='posthashtag',
            unique_together={('post', 'hashtag', 'platform')},
        ),

        # Add indexes for PostHashtag
        migrations.AddIndex(
            model_name='posthashtag',
            index=models.Index(fields=['post', 'hashtag'], name='post_hasht_post_id_idx'),
        ),
        migrations.AddIndex(
            model_name='posthashtag',
            index=models.Index(fields=['-impressions'], name='post_hasht_impress_idx'),
        ),

        # HashtagPerformanceSnapshot model
        migrations.CreateModel(
            name='HashtagPerformanceSnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('snapshot_date', models.DateField(verbose_name='Snapshot Date')),
                ('daily_uses', models.PositiveIntegerField(default=0, verbose_name='Daily Uses')),
                ('daily_posts', models.PositiveIntegerField(default=0, verbose_name='Daily Posts')),
                ('daily_impressions', models.BigIntegerField(default=0, verbose_name='Daily Impressions')),
                ('daily_engagements', models.BigIntegerField(default=0, verbose_name='Daily Engagements')),
                ('daily_clicks', models.BigIntegerField(default=0, verbose_name='Daily Clicks')),
                ('trending_rank', models.PositiveIntegerField(blank=True, null=True, verbose_name='Trending Rank')),
                ('hashtag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_snapshots', to='social_media.hashtag', verbose_name='Hashtag')),
            ],
            options={
                'verbose_name': 'Hashtag Performance Snapshot',
                'verbose_name_plural': 'Hashtag Performance Snapshots',
                'db_table': 'hashtag_performance_snapshots',
                'ordering': ['-snapshot_date', 'trending_rank'],
            },
        ),

        migrations.AlterUniqueTogether(
            name='hashtagperformancesnapshot',
            unique_together={('hashtag', 'snapshot_date')},
        ),

        # Add indexes for HashtagPerformanceSnapshot
        migrations.AddIndex(
            model_name='hashtagperformancesnapshot',
            index=models.Index(fields=['-snapshot_date'], name='hashtag_pe_snapsho_idx'),
        ),
        migrations.AddIndex(
            model_name='hashtagperformancesnapshot',
            index=models.Index(fields=['trending_rank'], name='hashtag_pe_trendin_idx'),
        ),
    ]
