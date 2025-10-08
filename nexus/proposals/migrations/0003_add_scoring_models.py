# Generated migration file

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_add_reviewer_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewCriteria',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('weight', models.DecimalField(decimal_places=2, default=1.0, help_text='Weight of this criteria in overall score (e.g., 1.0, 1.5, 2.0)', max_digits=5, verbose_name='Weight')),
                ('max_score', models.PositiveIntegerField(default=5, help_text='Maximum score for this criteria', verbose_name='Max Score')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order', verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Review Criteria',
                'verbose_name_plural': 'Review Criteria',
                'db_table': 'review_criteria',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ProposalScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('score', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Score')),
                ('notes', models.TextField(blank=True, help_text='Optional notes about this score', verbose_name='Notes')),
                ('criteria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='scores', to='proposals.reviewcriteria', verbose_name='Criteria')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='proposals.proposalreview', verbose_name='Review')),
            ],
            options={
                'verbose_name': 'Proposal Score',
                'verbose_name_plural': 'Proposal Scores',
                'db_table': 'proposal_scores',
                'ordering': ['criteria__order'],
            },
        ),
        migrations.CreateModel(
            name='ProposalOverallScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('average_score', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Average Score')),
                ('weighted_average', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Weighted Average')),
                ('total_reviews', models.PositiveIntegerField(default=0, verbose_name='Total Reviews')),
                ('last_calculated_at', models.DateTimeField(auto_now=True, verbose_name='Last Calculated At')),
                ('proposal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='overall_score', to='proposals.proposal', verbose_name='Proposal')),
            ],
            options={
                'verbose_name': 'Proposal Overall Score',
                'verbose_name_plural': 'Proposal Overall Scores',
                'db_table': 'proposal_overall_scores',
                'ordering': ['-weighted_average'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='proposalscore',
            unique_together={('review', 'criteria')},
        ),
    ]
