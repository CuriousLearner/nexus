# Third Party Stuff
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class AuditLog(TimeStampedUUIDModel):
    """Model to track all administrative actions"""

    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('publish', 'Publish'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('User')
    )
    action = models.CharField(_('Action'), max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(_('Description'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)

    # Generic foreign key to track any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Store changes as JSON
    changes = models.JSONField(_('Changes'), default=dict, blank=True,
                              help_text='JSON representation of what changed')

    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        user_email = self.user.email if self.user else 'Anonymous'
        return f'{user_email} - {self.action} - {self.created_at}'

    @classmethod
    def log_action(cls, user, action, description='', content_object=None, changes=None,
                   ip_address=None, user_agent=''):
        """Helper method to create audit log entries"""
        log_data = {
            'user': user,
            'action': action,
            'description': description,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'changes': changes or {},
        }

        if content_object:
            log_data['content_object'] = content_object

        return cls.objects.create(**log_data)
