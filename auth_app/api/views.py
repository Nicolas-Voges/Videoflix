from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from auth_app.api.serializers import RegisterSerializer

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

User = get_user_model()
class ActivationView(APIView):
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