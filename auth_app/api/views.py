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

from auth_app.api.serializers import RegisterSerializer, EmailLoginTokenObtainPairSerializer,\
PasswordResetSerializer
from auth_app.utils import send_mail, create_uidb64_and_token

from auth_app.api.serializers import RegisterSerializer, EmailLoginTokenObtainPairSerializer

class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


User = get_user_model()
class ActivationAPIView(APIView):
    def get(self, request, uidb64, token):
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
    """Obtain JWT tokens and set them as HttpOnly cookies.

    On successful authentication the view sets two cookies
    (``access_token`` and ``refresh_token``) and returns a JSON object
    with a success message and basic user information.
    """

    permission_classes = [AllowAny]
    serializer_class = EmailLoginTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Authenticate the user and return tokens as cookies."""

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
    """Refresh the access token using the refresh token stored in a cookie.

    The view reads the refresh token from the cookie ``refresh_token`` and
    returns a new access token in the response body and as an
    HttpOnly cookie. If the cookie is missing or invalid, the view
    returns HTTP 401.
    """

    def post(self, request, *args, **kwargs):
        """Handle POST to refresh the access token."""
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response(
                {'detail': 'Refresh token not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

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
    """Blacklist the refresh token stored in the cookie and clear cookies.

    This view overrides the serializer construction to pull the refresh
    token from the request cookies. After delegating to the parent
    class to blacklist the token, it deletes the token cookies and
    returns a friendly success message.
    """

    def get_serializer(self, *args, **kwargs):
        """Return a TokenBlacklistSerializer populated with the cookie token.

        Raises AuthenticationFailed if no refresh token cookie is present.
        """
        refresh_token = self.request.COOKIES.get('refresh_token')
        if refresh_token is None:
            raise AuthenticationFailed("Not authenticated.")
        kwargs['data'] = {'refresh': refresh_token}
        return TokenBlacklistSerializer(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        """Blacklist the refresh token and clear auth cookies.

        Returns a 200 response with a confirmation message.
        """
        response = super().post(request, *args, **kwargs)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.data = {'detail': "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}
        return response
    
class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
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

        return Response(
            {"detail": "Password reset email sent."},
            status=status.HTTP_200_OK
        )