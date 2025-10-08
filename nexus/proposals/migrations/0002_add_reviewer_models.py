# Generated migration file

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalReviewer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('assigned_at', models.DateTimeField(auto_now_add=True, verbose_name='Assigned At')),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewer_assignments', to=settings.AUTH_USER_MODEL, verbose_name='Assigned By')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewers', to='proposals.proposal', verbose_name='Proposal')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewed_proposals', to=settings.AUTH_USER_MODEL, verbose_name='Reviewer')),
            ],
            options={
                'verbose_name': 'Proposal Reviewer',
                'verbose_name_plural': 'Proposal Reviewers',
                'db_table': 'proposal_reviewers',
                'ordering': ['-assigned_at'],
            },
        ),
        migrations.CreateModel(
            name='ProposalReview',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20, verbose_name='Status')),
                ('recommendation', models.CharField(blank=True, choices=[('strong_accept', 'Strong Accept'), ('accept', 'Accept'), ('borderline', 'Borderline'), ('reject', 'Reject'), ('strong_reject', 'Strong Reject')], max_length=20, null=True, verbose_name='Recommendation')),
                ('comments', models.TextField(blank=True, help_text='Private comments for organizers', verbose_name='Comments')),
                ('feedback_for_speaker', models.TextField(blank=True, help_text='Public feedback that will be shared with speaker', verbose_name='Feedback for Speaker')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='Reviewed At')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='proposals.proposal', verbose_name='Proposal')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposal_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Reviewer')),
            ],
            options={
                'verbose_name': 'Proposal Review',
                'verbose_name_plural': 'Proposal Reviews',
                'db_table': 'proposal_reviews',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='proposalreviewer',
            unique_together={('proposal', 'reviewer')},
        ),
        migrations.AlterUniqueTogether(
            name='proposalreview',
            unique_together={('proposal', 'reviewer')},
        ),
    ]
