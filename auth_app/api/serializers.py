"""Serializers for authentication-related API endpoints.

This module provides a serializer for user registration used by the
registration API. It performs basic validation and creates a new
User instance when saved.
"""

import re
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer used to register a new user.

    Validation ensures that the password and confirmed_password match
    and that the email address is unique among existing users.
    """
    
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']

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
    

    def validate(self, data):
        """
        Ensure the username derived from the email is unique.

        Raises:
            serializers.ValidationError: If the username already exists.

        Returns:
            dict: The validated data.
        """
        email = data.get('email')
        username = re.sub(r'[^.\w@+-]', '_', email)

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "Dieser Benutzername existiert bereits."}
            )
        return data


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

        # Append a numeric suffix if the username already exists
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        validated_data['username'] = username
        validated_data['is_active'] = False
        user = User.objects.create_user(**validated_data)
        return user


class EmailLoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'username' in self.fields:
            self.fields.pop('username')


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")
        
        if not user.is_active:
            raise serializers.ValidationError("Confirm your email address to activate your account!")
        
        data = super().validate({'username': user.username, 'password': password})
        return data
    

class PasswordResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email']

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError({'detail': "Wrong email address"})
        return value