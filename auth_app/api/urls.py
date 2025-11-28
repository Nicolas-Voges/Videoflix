"""
URL configuration for API endpoints related to authentication.

This module defines the following public routes:
- Registration and account activation
- Email-based JWT authentication (login, refresh, logout)
- Password reset request and confirmation
"""

from django.urls import path

from .views import RegisterAPIView, ActivationAPIView, LoginTokenObtainPairView,\
AccessTokenRefreshView, LogoutTokenBlacklistView, PasswordResetAPIView, PasswordResetConfirmAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name="register"),
    path('activate/<str:uidb64>/<str:token>/', ActivationAPIView.as_view(), name="activate"),
    path('login/', LoginTokenObtainPairView.as_view(), name="login"),
    path('token/refresh/', AccessTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutTokenBlacklistView.as_view(), name='logout'),
    path('password_reset/', PasswordResetAPIView.as_view(), name='password_reset'),
    path('password_reset_confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmAPIView.as_view(), name='password_confirm')
]