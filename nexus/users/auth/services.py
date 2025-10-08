# Third Party Stuff
from django.conf import settings
from mail_templated import EmailMessage

# nexus Stuff
from nexus.users.tokens import PasswordResetToken, EmailVerificationToken
from .tokens import get_token_for_password_reset


def send_password_reset_mail(user, template_name='emails/password_reset.html'):
    """Send password reset email with token"""
    reset_token = PasswordResetToken.generate_token(user)
    ctx = {
        'user': user,
        'token': reset_token.token,
        'reset_url': f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}",
    }

    message = EmailMessage(
        template_name,
        ctx,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    return message.send()


def send_email_verification_mail(user, template_name='emails/email_verification.html'):
    """Send email verification with token"""
    verification_token = EmailVerificationToken.generate_token(user)
    ctx = {
        'user': user,
        'token': verification_token.token,
        'verification_url': f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}",
    }

    message = EmailMessage(
        template_name,
        ctx,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    return message.send()
