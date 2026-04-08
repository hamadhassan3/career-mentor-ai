import os
import pyotp
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TOTPDevice
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    TOTPVerifySerializer,
    TOTPLoginSerializer,
    ChangePasswordSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginView(APIView):
    """Custom login that handles TOTP two-factor authentication."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        has_confirmed_totp = hasattr(user, 'totp_device') and user.totp_device.confirmed

        if has_confirmed_totp:
            # User has TOTP set up — require second factor
            totp_token = signing.dumps(user.pk, salt='totp-login')
            return Response({
                'totp_required': True,
                'totp_token': totp_token,
            })
        else:
            # No TOTP yet — issue tokens and flag that setup is needed
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'totp_setup_required': True,
            })


class TOTPLoginVerifyView(APIView):
    """Verify TOTP code during login to get JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TOTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_pk = signing.loads(
                serializer.validated_data['totp_token'],
                salt='totp-login',
                max_age=300,  # 5 minute expiry
            )
            user = User.objects.get(pk=user_pk)
        except (signing.BadSignature, User.DoesNotExist):
            return Response(
                {'detail': 'Invalid or expired TOTP token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not hasattr(user, 'totp_device') or not user.totp_device.confirmed:
            return Response(
                {'detail': 'TOTP is not set up for this user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        totp = pyotp.TOTP(user.totp_device.secret)
        if not totp.verify(serializer.validated_data['code'], valid_window=1):
            return Response(
                {'detail': 'Invalid TOTP code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class TOTPSetupView(APIView):
    """Generate a TOTP secret and provisioning URI for the authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        device, created = TOTPDevice.objects.get_or_create(
            user=request.user,
            defaults={'secret': pyotp.random_base32()},
        )

        # If they're re-doing setup (not yet confirmed), regenerate the secret
        if not created and not device.confirmed:
            device.secret = pyotp.random_base32()
            device.save()

        totp = pyotp.TOTP(device.secret)
        provisioning_uri = totp.provisioning_uri(
            name=request.user.email or request.user.username,
            issuer_name=os.getenv('APP_NAME', 'Career Mentor'),
        )

        return Response({
            'provisioning_uri': provisioning_uri,
            'secret': device.secret,
        })


class TOTPConfirmView(APIView):
    """Confirm TOTP setup by verifying a code from the authenticator app."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TOTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            device = request.user.totp_device
        except TOTPDevice.DoesNotExist:
            return Response(
                {'detail': 'TOTP has not been set up. Call the setup endpoint first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        totp = pyotp.TOTP(device.secret)
        if not totp.verify(serializer.validated_data['code'], valid_window=1):
            return Response(
                {'detail': 'Invalid code. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device.confirmed = True
        device.save()
        return Response({'detail': 'TOTP has been enabled successfully.'})


class ChangePasswordView(APIView):
    """Change password for the authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data['current_password']):
            return Response(
                {'detail': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password changed successfully.'})


class PasswordResetRequestView(APIView):
    """Send a password reset email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Always return success to prevent email enumeration
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

            send_mail(
                subject=f'{os.getenv("APP_NAME", "Career Mentor")} - Password Reset',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except User.DoesNotExist:
            pass

        return Response({'detail': 'If an account with that email exists, a reset link has been sent.'})


class PasswordResetConfirmView(APIView):
    """Reset the password using uid and token from the email link."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = urlsafe_base64_decode(serializer.validated_data['uid']).decode()
            user = User.objects.get(pk=uid)
        except (ValueError, User.DoesNotExist):
            return Response(
                {'detail': 'Invalid reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, serializer.validated_data['token']):
            return Response(
                {'detail': 'Invalid or expired reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password has been reset successfully.'})
