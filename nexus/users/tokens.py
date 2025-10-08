# Standard Library
import binascii
import os
from datetime import timedelta

# Third Party Stuff
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PasswordResetToken(models.Model):
    """Model to store password reset tokens"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='password_reset_tokens')
    token = models.CharField(_('Token'), max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expires At'))
    is_used = models.BooleanField(_('Is Used'), default=False)

    class Meta:
        verbose_name = _('Password Reset Token')
        verbose_name_plural = _('Password Reset Tokens')
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.token[:8]}...'

    @classmethod
    def generate_token(cls, user, expiry_hours=24):
        """Generate a new password reset token for user"""
        token = binascii.hexlify(os.urandom(32)).decode()
        expires_at = timezone.now() + timedelta(hours=expiry_hours)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save()


class EmailVerificationToken(models.Model):
    """Model to store email verification tokens"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='email_verification_tokens')
    token = models.CharField(_('Token'), max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expires At'))
    is_used = models.BooleanField(_('Is Used'), default=False)

    class Meta:
        verbose_name = _('Email Verification Token')
        verbose_name_plural = _('Email Verification Tokens')
        db_table = 'email_verification_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.token[:8]}...'

    @classmethod
    def generate_token(cls, user, expiry_hours=48):
        """Generate a new email verification token for user"""
        token = binascii.hexlify(os.urandom(32)).decode()
        expires_at = timezone.now() + timedelta(hours=expiry_hours)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save()
