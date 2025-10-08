# Third Party Stuff
from django.contrib.auth import logout
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

# nexus Stuff
from nexus.base import response
from nexus.base.api.mixins import MultipleSerializerMixin
from nexus.users import services as user_services

from . import serializers, services, tokens


class AuthViewSet(MultipleSerializerMixin, viewsets.GenericViewSet):

    permission_classes = [AllowAny, ]
    serializer_classes = {
        'login': serializers.LoginSerializer,
        'register': serializers.RegisterSerializer,
        'logout': serializers.EmptySerializer,
        'password_change': serializers.PasswordChangeSerializer,
        'password_reset': serializers.PasswordResetSerializer,
        'password_reset_confirm': serializers.PasswordResetConfirmSerializer,
    }

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.get_and_authenticate_user(**serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return response.Ok(data)

    @action(methods=['POST', ], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.create_user_account(**serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return response.Created(data)

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        """
        Calls Django logout method; Does not work for UserTokenAuth.
        """
        logout(request)
        return response.Ok({"success": "Successfully logged out."})

    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return response.NoContent()

    @action(methods=['POST', ], detail=False)
    def password_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.get_user_by_email(serializer.data['email'])
        if user:
            services.send_password_reset_mail(user)
        return response.Ok({'message': 'Further instructions will be sent to the email if it exists'})

    @action(methods=['POST', ], detail=False)
    def password_reset_confirm(self, request):
        from nexus.users.tokens import PasswordResetToken
        from nexus.base import exceptions as exc

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reset_token = PasswordResetToken.objects.get(token=serializer.validated_data['token'])
            if not reset_token.is_valid():
                raise exc.BadRequest('Token is invalid or expired')

            user = reset_token.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            reset_token.mark_as_used()
            return response.NoContent()
        except PasswordResetToken.DoesNotExist:
            raise exc.BadRequest('Invalid token')

    @action(methods=['POST', ], detail=False)
    def verify_email(self, request):
        from nexus.users.tokens import EmailVerificationToken
        from nexus.base import exceptions as exc
        from rest_framework import serializers as drf_serializers

        class VerifyEmailSerializer(drf_serializers.Serializer):
            token = drf_serializers.CharField()

        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            verification_token = EmailVerificationToken.objects.get(token=serializer.validated_data['token'])
            if not verification_token.is_valid():
                raise exc.BadRequest('Token is invalid or expired')

            user = verification_token.user
            user.is_active = True
            user.save()
            verification_token.mark_as_used()
            return response.Ok({'message': 'Email verified successfully'})
        except EmailVerificationToken.DoesNotExist:
            raise exc.BadRequest('Invalid token')

    @action(methods=['POST', ], detail=False)
    def resend_verification(self, request):
        from rest_framework import serializers as drf_serializers

        class ResendVerificationSerializer(drf_serializers.Serializer):
            email = drf_serializers.EmailField()

        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.get_user_by_email(serializer.validated_data['email'])
        if user and not user.is_active:
            services.send_email_verification_mail(user)
        return response.Ok({'message': 'Verification email sent if account exists and is unverified'})
