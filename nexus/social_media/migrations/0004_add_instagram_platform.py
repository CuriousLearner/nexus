# Generated migration file

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0003_add_post_analytics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='posted_at',
            field=models.CharField(
                choices=[('fb', 'Facebook'), ('twitter', 'Twitter'), ('linkedin', 'Linkedin'), ('instagram', 'Instagram')],
                max_length=10,
                verbose_name='Posted at platform'
            ),
        ),
    ]
