import time

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class RegisterTests(APITestCase):
    def setUp(self):
        self.user_email = "user@example.com"
        self.url = reverse('register')
        self.data = {
            'username': 'TestUser',
            'email': self.user_email,
            'password': "securepassword",
            'confirmed_password': "securepassword"
        }


    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_post_success(self):
        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_email).exists())
        self.assertFalse(User.objects.get(email=self.user_email).is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Confirm your email", mail.outbox[0].subject)
        self.assertIn(self.user_email, mail.outbox[0].to)

    
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_post_fails(self):
        data_invalid_password = {
            'email': "test@test.de",
            'password': "securepassword",
            'confirmed_password': "wrong"
        }
        data_invalid_email = {
            'email': self.user_email,
            'password': "securepassword",
            'confirmed_password': "securepassword"
        }
        # First, register the user successfully
        self.client.post(self.url, self.data, format='json')
        cases = [
            (data_invalid_password, status.HTTP_400_BAD_REQUEST),
            (data_invalid_email, status.HTTP_400_BAD_REQUEST),
        ]

        for data, expected_status in cases:
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, expected_status)

    
class AccountActivationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="TestUser",
            password="Test123$",
            email='test@test.de',
            is_active=False
        )
        self.uidb64 = urlsafe_base64_encode(str(self.user.pk).encode('utf-8'))
        self.token = default_token_generator.make_token(self.user)


    def test_get_success(self):
        response = self.client.get(reverse('activate', kwargs={"uidb64": self.uidb64, "token": self.token}))

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)


    def test_get_invalid_token(self):
        invalid_token = self.token + "x"

        response = self.client.get(reverse('activate', kwargs={"uidb64": self.uidb64, "token": invalid_token}))

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)


    @override_settings(PASSWORD_RESET_TIMEOUT=1)
    def test_get_expired_token(self):
        user = User.objects.create_user(
            username="NewUser",
            password="Test123$",
            email='new@new.de',
            is_active=False
        )
        uidb64 = urlsafe_base64_encode(str(user.pk).encode('utf-8'))
        token = default_token_generator.make_token(user)

        time.sleep(2)

        response = self.client.get(reverse('activate', kwargs={"uidb64": uidb64, "token": token}))

        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user.is_active)


class LoginTests(APITestCase):
    def setUp(self):
        self.email_active = "user@active.com"
        self.username_active = "ActiveTestUser"
        self.password = "Test123$"
        self.user_active = User.objects.create_user(
            username=self.username_active,
            password=self.password,
            email=self.email_active,
            is_active=True
        )

        self.email_not_active = "user@inactive.com"
        self.username_not_active = "InactiveTestUser"
        self.user_not_active = User.objects.create_user(
            username=self.username_not_active,
            password=self.password,
            email=self.email_not_active,
            is_active=False
        )

        self.url = reverse('login')


    def test_post_success(self):
        data = {
            'email': self.email_active,
            'password': self.password
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)


    def test_post_fails(self):
        cases = [
            ("wrong_password", {'email': self.email_active, 'password': 'wrong_password'}),
            ("wrong_email", {'email': 'wrong@wro.ng', 'password': self.password}),
            ("not_active_user", {'email': self.email_not_active, 'password': self.password})
        ]
        
        for message, data in cases:
            with self.subTest(test_case=message):
                response = self.client.post(self.url, data, format='json')

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertNotIn('access_token', response.cookies)
                self.assertNotIn('refresh_token', response.cookies)


class TokenRefreshTests(APITestCase):
    """Tests for refreshing the access token using the refresh cookie."""

    def setUp(self):
        self.username = 'test_user'
        self.password = 'test1234'
        self.email = 'test@web.de'
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        self.login_url = reverse('login')
        self.refresh_url = reverse('token_refresh')


    def test_post_success(self):
        """A logged-in client can refresh the access token successfully."""
        self.client.post(self.login_url, {'email': self.email, 'password': self.password}, format='json')

        response = self.client.post(self.refresh_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


    def test_post_fails_no_cookie(self):
        """If no refresh cookie is present, the view returns 401."""
        response = self.client.post(self.refresh_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Refresh token not provided.')


    def test_post_fails_invalid_token(self):
        """An invalid refresh cookie yields an unauthorized response."""
        self.client.cookies['refresh_token'] = 'invalid_token'
        response = self.client.post(self.refresh_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid refresh token.')