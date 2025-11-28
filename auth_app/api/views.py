"""
Views for API endpoints related to authentication.

This module provides:
- Registration and account activation
- Email-based login using JWT
- Token refresh and logout
- Password reset request and confirmation
"""

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework.exceptions import AuthenticationFailed

from auth_app.api.serializers import PasswordResetConfirmSerializer, RegisterSerializer,\
    EmailLoginTokenObtainPairSerializer, PasswordResetSerializer
from auth_app.utils import send_mail, create_uidb64_and_token

class RegisterAPIView(CreateAPIView):
    """"Register a new user and trigger activation email."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


User = get_user_model()
class ActivationAPIView(APIView):
    """Activate a user account using uidb64 and token."""

    def get(self, request, uidb64, token):
        """
        Validate activation token and activate the user.
        Returns:
            - 200 if successfully activated
            - 400 for invalid activation data
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid link"}, status=400)

        if default_token_generator.check_token(user, token):
            if user.is_active:
                return Response({"error": "Already activated"}, status=400)
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated."}, status=200)
        else:
            return Response({"error": "Invalid or expired token"}, status=400)
        

class LoginTokenObtainPairView(TokenObtainPairView):
    """
    Authenticate a user using email and set JWT tokens as HttpOnly cookies.
    
    Response includes:
    - user info (id, username, email)
    - access & refresh token as secure HttpOnly cookies
    """

    permission_classes = [AllowAny]
    serializer_class = EmailLoginTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Validate credentials and issue JWT cookies.
        Errors:
            - 401 if authentication fails (handled by serializer)
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access = serializer.validated_data['access']
        refresh = serializer.validated_data['refresh']

        response = Response({'detail': "Login successful"})

        user = User.objects.get(email=request.data.get('email'))

        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        response.data = {
            'detail': "Login successfully!",
            'user': {
                'id': user.pk,
                'username': user.username,
                'email': user.email
            }
        }

        return response
    

class AccessTokenRefreshView(TokenRefreshView):
    """
    Refresh the access token using the HttpOnly refresh token cookie.
    Returns:
        - New access token
    Errors:
        - 401 if refresh token missing or invalid
    """

    def post(self, request, *args, **kwargs):
        """Get refresh token from cookie, validate it, set new access cookie."""
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail': 'Refresh token not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data.get('access')

        response = Response({'detail': "Token refreshed", 'access': access_token}, status=status.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        return response
    

class LogoutTokenBlacklistView(TokenBlacklistView):
    """
    Log out the user by blacklisting the current refresh token.
    Removes cookies and prevents further authenticated access.
    """

    def get_serializer(self, *args, **kwargs):
        """Provide refresh token from cookie for blacklisting or raise error if missing."""
        refresh_token = self.request.COOKIES.get('refresh_token')
        if refresh_token is None:
            raise AuthenticationFailed("Not authenticated.")
        kwargs['data'] = {'refresh': refresh_token}
        return TokenBlacklistSerializer(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        """Blacklist token and clear both auth cookies."""
        response = super().post(request, *args, **kwargs)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.data = {'detail': "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}
        return response


class PasswordResetAPIView(APIView):
    """
    Initiate password reset by sending email with secure token.
    Always returns success to prevent email enumeration.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        """Send password reset email if account exists."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "An email has been sent to reset your password."}, status=status.HTTP_200_OK)
        
        uidb64, token = create_uidb64_and_token(user)

        send_mail(
            uidb64=uidb64,
            token=token,
            instance=user,
            content_type="reset_password"
        )

        return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)
    

class PasswordResetConfirmAPIView(APIView):
    """Verify token and set new password."""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        """
        Validate reset token and update password.
        Errors:
            - 400 invalid uid/token
        Success:
            - 200 confirmation message
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)