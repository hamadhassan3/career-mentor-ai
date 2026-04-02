from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    MeView,
    LoginView,
    TOTPLoginVerifyView,
    TOTPSetupView,
    TOTPConfirmView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
    # TOTP
    path('totp/setup/', TOTPSetupView.as_view(), name='totp_setup'),
    path('totp/confirm/', TOTPConfirmView.as_view(), name='totp_confirm'),
    path('totp/login/', TOTPLoginVerifyView.as_view(), name='totp_login'),
    # Password reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
