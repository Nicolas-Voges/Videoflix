import time

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.core import mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.user_mail = "user@example.com"
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.register_data = {
            'username': 'TestUser',
            'email': self.user_mail,
            'password': "securepassword",
            'confirmed_password': "securepassword"
        }

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_register_success(self):
        response = self.client.post(self.register_url, self.register_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_mail).exists())
        self.assertFalse(User.objects.get(email=self.user_mail).is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Confirm your email", mail.outbox[0].subject)
        self.assertIn(self.user_mail, mail.outbox[0].to)

    
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_register_fails(self):
        data_invalid_password = {
            'email': "test@test.de",
            'password': "securepassword",
            'confirmed_password': "wrong"
        }
        data_invalid_email = {
            'email': self.user_mail,
            'password': "securepassword",
            'confirmed_password': "securepassword"
        }
        # First, register the user successfully
        self.client.post(self.register_url, self.register_data, format='json')
        cases = [
            (data_invalid_password, status.HTTP_400_BAD_REQUEST),
            (data_invalid_email, status.HTTP_400_BAD_REQUEST),
        ]

        for data, expected_status in cases:
            response = self.client.post(self.register_url, data, format='json')
            self.assertEqual(response.status_code, expected_status)

    
    def test_activate_success(self):
        user = User.objects.create_user(
            username="TestUser",
            password="Test123$",
            email=self.user_mail,
            is_active=False
        )
        uidb64 = urlsafe_base64_encode(str(user.pk).encode('utf-8'))
        token = default_token_generator.make_token(user)
        response = self.client.get(reverse('activate', kwargs={"uidb64": uidb64, "token": token}))

        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.is_active)


    def test_activate_invalid_token(self):
        user = User.objects.create_user(
            username="TestUser",
            password="Test123$",
            email=self.user_mail,
            is_active=False
        )

        uidb64 = urlsafe_base64_encode(str(user.pk).encode('utf-8'))
        token = default_token_generator.make_token(user)
        invalid_token = token + "x"

        response = self.client.get(reverse('activate', kwargs={"uidb64": uidb64, "token": invalid_token}))

        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user.is_active)


    @override_settings(PASSWORD_RESET_TIMEOUT=1)
    def test_activate_expired_token(self):
        user = User.objects.create_user(
            username="TestUser",
            password="Test123$",
            email=self.user_mail,
            is_active=False
        )

        uidb64 = urlsafe_base64_encode(str(user.pk).encode('utf-8'))
        token = default_token_generator.make_token(user)

        time.sleep(2)

        response = self.client.get(reverse('activate', kwargs={"uidb64": uidb64, "token": token}))

        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user.is_active)


    def test_login_success(self):
        username = "TestUser"
        password = "Test123$"
        user = User.objects.create_user(
            username=username,
            password=password,
            email=self.user_mail,
            is_active=True
        )

        response = self.client.post(self.login_url, {'email': self.user_mail, 'password': password}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)


    def test_post_fails(self):
        username = "TestUser"
        password = "Test123$"
        user = User.objects.create_user(
            username=username,
            password=password,
            email=self.user_mail,
            is_active=True
        )
        user_mot_active = User.objects.create_user(
            username='username',
            password='password',
            email='new@mail.de',
            is_active=False
        )

        cases = [
            ("wrong_username", {'username': username, 'password': 'wrong_password'}),
            ("wrong_password", {'username': 'wrong', 'password': password}),
            ("inactive_user", {'username': 'username', 'password': 'password'})
        ]

        for message, data in cases:
            with self.subTest(test_case=message):
                response = self.client.post(self.url, data, format='json')

                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                self.assertNotIn('access_token', response.cookies)
                self.assertNotIn('refresh_token', response.cookies)