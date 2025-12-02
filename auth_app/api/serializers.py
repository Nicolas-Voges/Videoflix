"""
Serializers for authentication-related API endpoints.

This module contains serializers that handle user registration,
email-based authentication using JWT, and password reset functionality.

Classes:
    RegisterSerializer:
        Handles user registration, including email uniqueness validation
        and password confirmation checks. A unique username is derived
        from the user's email.

    EmailLoginTokenObtainPairSerializer:
        Extends TokenObtainPairSerializer to authenticate using an email
        instead of a username.

    PasswordResetSerializer:
        Validates the email during a password reset request.

    PasswordResetConfirmSerializer:
        Validates new password input including confirmation matching.
"""

import re

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer used to register a new user.

    This serializer ensures:
    - The password matches the confirmed_password field.
    - The provided email is unique in the User database.

    A unique username is automatically generated from the email address.
    The created user is initially set to inactive until verification.
    """
    
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']

        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }


    def validate_confirmed_password(self, value):
        """Ensure the password confirmation matches the password."""
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value


    def validate_email(self, value):
        """Validate that the email address is not already in use."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value


    def create(self, validated_data):
        """
        Create a new User with a unique username from the email.

        Returns:
            User: The newly created user instance.
        """
        
        validated_data.pop('confirmed_password')
        email = validated_data['email']
        base_username = re.sub(r'[^.\w@+-]', '_', email)
        username = base_username

        validated_data['username'] = username
        validated_data['is_active'] = False
        user = User.objects.create_user(**validated_data)
        return user


class EmailLoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Authenticate users via email instead of username.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        """Remove username field from serializer."""
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)


    def validate(self, attrs):
        """Validate email, password and active status."""
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password or your account is not active!")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password or your account is not active!")
        
        if not user.is_active:
            raise serializers.ValidationError("Invalid email or password or your account is not active!")
        
        return super().validate({
            'username': user.username,
            'password': password
        })
    

class PasswordResetSerializer(serializers.Serializer):
    """Validate email for password reset request."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Ensure new password and confirmation match."""
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs