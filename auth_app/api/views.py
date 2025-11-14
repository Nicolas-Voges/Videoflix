from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed

from auth_app.api.serializers import RegisterSerializer, EmailTokenObtainPairSerializer

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
    serializer_class = EmailTokenObtainPairSerializer
    
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