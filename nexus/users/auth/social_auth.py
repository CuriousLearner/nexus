# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _

# Nexus Stuff
from nexus.base.models import TimeStampedUUIDModel


class SocialAccount(TimeStampedUUIDModel):
    """Social media account connections for OAuth login"""

    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='social_accounts',
                            verbose_name=_('User'))

    # Provider details
    provider = models.CharField(_('Provider'), max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(_('Provider User ID'), max_length=255,
                                       db_index=True)

    # OAuth tokens
    access_token = models.TextField(_('Access Token'), blank=True)
    refresh_token = models.TextField(_('Refresh Token'), blank=True)
    token_expires_at = models.DateTimeField(_('Token Expires At'), null=True, blank=True)

    # Profile data
    email = models.EmailField(_('Email'), blank=True)
    username = models.CharField(_('Username'), max_length=255, blank=True)
    profile_url = models.URLField(_('Profile URL'), blank=True)
    avatar_url = models.URLField(_('Avatar URL'), blank=True)
    extra_data = models.JSONField(_('Extra Data'), default=dict,
                                  help_text='Additional profile data from provider')

    # Status
    is_verified = models.BooleanField(_('Is Verified'), default=False)
    last_login = models.DateTimeField(_('Last Login'), null=True, blank=True)

    class Meta:
        verbose_name = _('Social Account')
        verbose_name_plural = _('Social Accounts')
        db_table = 'social_accounts'
        unique_together = [['provider', 'provider_user_id']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'provider']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.get_provider_display()}'

    def refresh_access_token(self):
        """Refresh OAuth access token"""
        # This would integrate with OAuth provider APIs
        # Implementation depends on specific provider
        pass


class OAuthState(TimeStampedUUIDModel):
    """Temporary OAuth state for CSRF protection"""

    state = models.CharField(_('State'), max_length=255, unique=True, db_index=True)
    provider = models.CharField(_('Provider'), max_length=20)

    # Request details
    next_url = models.CharField(_('Next URL'), max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(_('IP Address'))

    # Expiry
    expires_at = models.DateTimeField(_('Expires At'))
    used = models.BooleanField(_('Used'), default=False)

    class Meta:
        verbose_name = _('OAuth State')
        verbose_name_plural = _('OAuth States')
        db_table = 'oauth_states'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.provider} - {self.state[:8]}...'


def validate_password_strength(password):
    """
    Validate password strength

    :param password: Password to validate
    :returns: Dict with is_valid and errors
    """
    errors = []
    is_valid = True

    # Minimum length
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
        is_valid = False

    # Maximum length
    if len(password) > 128:
        errors.append('Password must not exceed 128 characters')
        is_valid = False

    # Must contain uppercase
    if not any(c.isupper() for c in password):
        errors.append('Password must contain at least one uppercase letter')
        is_valid = False

    # Must contain lowercase
    if not any(c.islower() for c in password):
        errors.append('Password must contain at least one lowercase letter')
        is_valid = False

    # Must contain digit
    if not any(c.isdigit() for c in password):
        errors.append('Password must contain at least one number')
        is_valid = False

    # Must contain special character
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    if not any(c in special_chars for c in password):
        errors.append('Password must contain at least one special character')
        is_valid = False

    # Check for common passwords
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890'
    ]
    if password.lower() in common_passwords:
        errors.append('This password is too common. Please choose a more unique password')
        is_valid = False

    # Check for sequential characters
    sequential_patterns = ['abc', '123', 'qwe', 'asd', 'zxc']
    password_lower = password.lower()
    if any(pattern in password_lower for pattern in sequential_patterns):
        errors.append('Password should not contain sequential characters')
        is_valid = False

    return {
        'is_valid': is_valid,
        'errors': errors,
        'strength': calculate_password_strength(password)
    }


def calculate_password_strength(password):
    """
    Calculate password strength score

    :param password: Password to evaluate
    :returns: String (weak, fair, good, strong, very_strong)
    """
    score = 0

    # Length score
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1

    # Character variety
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(not c.isalnum() for c in password):
        score += 1

    # Uniqueness (check for repeated characters)
    unique_chars = len(set(password))
    if unique_chars > len(password) * 0.7:
        score += 1

    # Map score to strength
    if score <= 2:
        return 'weak'
    elif score <= 4:
        return 'fair'
    elif score <= 6:
        return 'good'
    elif score <= 7:
        return 'strong'
    else:
        return 'very_strong'


class AccountRecovery(TimeStampedUUIDModel):
    """Account recovery requests"""

    RECOVERY_TYPE_CHOICES = [
        ('password_reset', 'Password Reset'),
        ('account_locked', 'Account Locked'),
        ('2fa_lost', '2FA Device Lost'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='recovery_requests',
                            verbose_name=_('User'))

    # Request details
    recovery_type = models.CharField(_('Recovery Type'), max_length=20,
                                    choices=RECOVERY_TYPE_CHOICES)
    reason = models.TextField(_('Reason'))

    # Verification
    verification_method = models.CharField(_('Verification Method'), max_length=50,
                                          blank=True)
    verification_data = models.JSONField(_('Verification Data'), default=dict)

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES,
                             default='pending')

    # Processing
    reviewed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='reviewed_recoveries',
                                   verbose_name=_('Reviewed By'))
    reviewed_at = models.DateTimeField(_('Reviewed At'), null=True, blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)

    # Security
    ip_address = models.GenericIPAddressField(_('IP Address'))
    user_agent = models.TextField(_('User Agent'), blank=True)

    class Meta:
        verbose_name = _('Account Recovery')
        verbose_name_plural = _('Account Recoveries')
        db_table = 'account_recoveries'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.get_recovery_type_display()}'


class UserActivityLog(TimeStampedUUIDModel):
    """Log user activities for security and audit"""

    ACTIVITY_TYPE_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('email_change', 'Email Change'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('profile_update', 'Profile Update'),
        ('social_account_connected', 'Social Account Connected'),
        ('social_account_disconnected', 'Social Account Disconnected'),
        ('session_revoked', 'Session Revoked'),
        ('account_recovery', 'Account Recovery Request'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                            related_name='activity_logs',
                            verbose_name=_('User'))

    # Activity details
    activity_type = models.CharField(_('Activity Type'), max_length=50,
                                    choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField(_('Description'), blank=True)
    metadata = models.JSONField(_('Metadata'), default=dict)

    # Request info
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    location = models.CharField(_('Location'), max_length=200, blank=True)

    class Meta:
        verbose_name = _('User Activity Log')
        verbose_name_plural = _('User Activity Logs')
        db_table = 'user_activity_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.get_activity_type_display()}'
