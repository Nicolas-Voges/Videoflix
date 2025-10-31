"""Serializers for authentication-related API endpoints.

This module provides a serializer for user registration used by the
registration API. It performs basic validation and creates a new
User instance when saved.
"""

import re
from rest_framework import serializers
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
        user = User.objects.create_user(**validated_data)
        return user