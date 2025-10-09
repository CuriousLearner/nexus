# Standard Library
import secrets
import time
from base64 import b32encode

# Third Party Stuff
import pyotp
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class TwoFactorAuth(TimeStampedUUIDModel):
    """Two-factor authentication settings for users"""

    METHOD_CHOICES = [
        ('totp', 'Authenticator App (TOTP)'),
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]

    user = models.OneToOneField('users.User', on_delete=models.CASCADE,
                                related_name='two_factor',
                                verbose_name=_('User'))

    # Settings
    is_enabled = models.BooleanField(_('Is Enabled'), default=False)
    method = models.CharField(_('Method'), max_length=20, choices=METHOD_CHOICES,
                             default='totp')

    # TOTP settings
    totp_secret = models.CharField(_('TOTP Secret'), max_length=32, blank=True)
    backup_codes = models.JSONField(_('Backup Codes'), default=list,
                                   help_text='List of one-time backup codes')

    # Phone for SMS
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    phone_verified = models.BooleanField(_('Phone Verified'), default=False)

    # Status
    verified_at = models.DateTimeField(_('Verified At'), null=True, blank=True)
    last_used_at = models.DateTimeField(_('Last Used At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Two-Factor Authentication')
        verbose_name_plural = _('Two-Factor Authentications')
        db_table = 'two_factor_auth'

    def __str__(self):
        return f'{self.user.email} - 2FA ({self.method})'

    def generate_totp_secret(self):
        """Generate new TOTP secret"""
        random_bytes = secrets.token_bytes(20)
        self.totp_secret = b32encode(random_bytes).decode('utf-8')
        self.save()
        return self.totp_secret

    def get_totp_uri(self):
        """Get TOTP provisioning URI for QR code"""
        if not self.totp_secret:
            self.generate_totp_secret()

        app_name = getattr(settings, 'SITE_NAME', 'Nexus')
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.user.email,
            issuer_name=app_name
        )

    def verify_totp_code(self, code):
        """Verify TOTP code"""
        if not self.totp_secret:
            return False

        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(code, valid_window=1)

    def generate_backup_codes(self, count=10):
        """Generate backup codes"""
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice('0123456789') for _ in range(8))
            # Format as XXXX-XXXX
            formatted_code = f'{code[:4]}-{code[4:]}'
            codes.append(formatted_code)

        self.backup_codes = codes
        self.save()
        return codes

    def use_backup_code(self, code):
        """Use a backup code (one-time use)"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False

    def send_sms_code(self):
        """Send SMS code (would integrate with Twilio)"""
        if not self.phone_number or not self.phone_verified:
            return False

        # Generate 6-digit code
        code = ''.join(secrets.choice('0123456789') for _ in range(6))

        # Store in cache for 5 minutes
        cache_key = f'2fa_sms_{self.user.id}'
        cache.set(cache_key, code, 300)

        # TODO: Integrate with Twilio to send SMS
        # For now, just log it
        print(f'SMS Code for {self.user.email}: {code}')

        return True

    def verify_sms_code(self, code):
        """Verify SMS code"""
        cache_key = f'2fa_sms_{self.user.id}'
        stored_code = cache.get(cache_key)

        if stored_code and stored_code == code:
            cache.delete(cache_key)
            return True
        return False

    def send_email_code(self):
        """Send email code"""
        # Generate 6-digit code
        code = ''.join(secrets.choice('0123456789') for _ in range(6))

        # Store in cache for 5 minutes
        cache_key = f'2fa_email_{self.user.id}'
        cache.set(cache_key, code, 300)

        # TODO: Send email with code
        print(f'Email Code for {self.user.email}: {code}')

        return True

    def verify_email_code(self, code):
        """Verify email code"""
        cache_key = f'2fa_email_{self.user.id}'
        stored_code = cache.get(cache_key)

        if stored_code and stored_code == code:
            cache.delete(cache_key)
            return True
        return False


class LoginAttempt(TimeStampedUUIDModel):
    """Track login attempts for security monitoring"""

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
        ('2fa_required', '2FA Required'),
        ('2fa_failed', '2FA Failed'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            null=True, blank=True,
                            related_name='login_attempts',
                            verbose_name=_('User'))

    # Attempt details
    email = models.EmailField(_('Email'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES)

    # Request metadata
    ip_address = models.GenericIPAddressField(_('IP Address'))
    user_agent = models.TextField(_('User Agent'), blank=True)
    country_code = models.CharField(_('Country Code'), max_length=2, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)

    # Failure reason
    failure_reason = models.CharField(_('Failure Reason'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('Login Attempt')
        verbose_name_plural = _('Login Attempts')
        db_table = 'login_attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['email', '-created_at']),
        ]

    def __str__(self):
        return f'{self.email} - {self.status} - {self.created_at}'

    @staticmethod
    def is_ip_blocked(ip_address):
        """Check if IP is temporarily blocked"""
        cache_key = f'blocked_ip_{ip_address}'
        return cache.get(cache_key, False)

    @staticmethod
    def block_ip(ip_address, duration=3600):
        """Block IP address temporarily"""
        cache_key = f'blocked_ip_{ip_address}'
        cache.set(cache_key, True, duration)

    @staticmethod
    def check_failed_attempts(email=None, ip_address=None, minutes=15, max_attempts=5):
        """Check for excessive failed attempts"""
        from datetime import timedelta

        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        attempts = LoginAttempt.objects.filter(
            created_at__gte=cutoff_time,
            status='failed'
        )

        if email:
            attempts = attempts.filter(email=email)
        if ip_address:
            attempts = attempts.filter(ip_address=ip_address)

        return attempts.count() >= max_attempts


class UserSession(TimeStampedUUIDModel):
    """Track user sessions across devices"""

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='sessions',
                            verbose_name=_('User'))

    # Session details
    session_key = models.CharField(_('Session Key'), max_length=40, unique=True,
                                   db_index=True)
    expires_at = models.DateTimeField(_('Expires At'))

    # Device info
    device_name = models.CharField(_('Device Name'), max_length=200, blank=True)
    device_type = models.CharField(_('Device Type'), max_length=20,
                                   choices=[
                                       ('desktop', 'Desktop'),
                                       ('mobile', 'Mobile'),
                                       ('tablet', 'Tablet'),
                                       ('unknown', 'Unknown'),
                                   ], default='unknown')
    browser = models.CharField(_('Browser'), max_length=100, blank=True)
    os = models.CharField(_('Operating System'), max_length=100, blank=True)

    # Location
    ip_address = models.GenericIPAddressField(_('IP Address'))
    country_code = models.CharField(_('Country Code'), max_length=2, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)

    # Status
    is_active = models.BooleanField(_('Is Active'), default=True)
    last_activity = models.DateTimeField(_('Last Activity'), auto_now=True)

    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        db_table = 'user_sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', '-last_activity']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.device_name or self.device_type}'

    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at

    def revoke(self):
        """Revoke this session"""
        self.is_active = False
        self.save()


class PasswordHistory(TimeStampedUUIDModel):
    """Track password history to prevent reuse"""

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='password_history',
                            verbose_name=_('User'))

    # Password hash (stored for comparison)
    password_hash = models.CharField(_('Password Hash'), max_length=255)

    # Metadata
    changed_from_ip = models.GenericIPAddressField(_('Changed From IP'), null=True, blank=True)

    class Meta:
        verbose_name = _('Password History')
        verbose_name_plural = _('Password Histories')
        db_table = 'password_history'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.created_at.date()}'

    @staticmethod
    def can_use_password(user, password_hash, history_count=5):
        """Check if password was used recently"""
        recent_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:history_count]

        return password_hash not in [ph.password_hash for ph in recent_passwords]
