# Generated migration file

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0004_add_instagram_platform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='posted_at',
            field=models.CharField(
                blank=True,
                choices=[('fb', 'Facebook'), ('twitter', 'Twitter'), ('linkedin', 'Linkedin'), ('instagram', 'Instagram')],
                help_text='Leave empty for multi-platform posting',
                max_length=10,
                null=True,
                verbose_name='Posted at platform'
            ),
        ),
        migrations.AddField(
            model_name='post',
            name='platforms',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of platforms for multi-platform posting. Use when posted_at is empty.',
                verbose_name='Platforms'
            ),
        ),
    ]
