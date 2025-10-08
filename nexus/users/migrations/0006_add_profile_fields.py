# Generated migration file

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_add_password_reset_tokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_photo',
            field=models.ImageField(blank=True, help_text='User profile photo', null=True, upload_to='profile_photos/', verbose_name='Profile Photo'),
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, default='', help_text='User biography', verbose_name='Bio'),
        ),
        migrations.AddField(
            model_name='user',
            name='twitter_handle',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Twitter Handle'),
        ),
        migrations.AddField(
            model_name='user',
            name='linkedin_url',
            field=models.URLField(blank=True, default='', verbose_name='LinkedIn URL'),
        ),
        migrations.AddField(
            model_name='user',
            name='github_username',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='GitHub Username'),
        ),
        migrations.AddField(
            model_name='user',
            name='website',
            field=models.URLField(blank=True, default='', verbose_name='Website'),
        ),
    ]
