from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.core import mail

from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.user_mail = "user@example.com"
        self.register_url = reverse('register')
        self.register_data = {
            'email': self.user_mail,
            'password': "securepassword",
            'confirmed_password': "securepassword"
        }
        
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_register_success(self):
        response = self.client.post(self.register_url, self.register_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_mail).exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Confirm your email", mail.outbox[0].subject)
        self.assertIn(self.user_mail, mail.outbox[0].to)