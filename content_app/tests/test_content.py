from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from content_app.models import Video

User = get_user_model()

class ContentListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Test123$', email='testuser@example.com')
        self.client.login(username='testuser', password='Test123$')
        self.url = reverse('content-list')
        self.expected_fields = {'id', 'created_at', 'title', 'description', 'thumbnail_url', 'category'}
        self.video = Video.objects.create(
            title="Sample Video",
            description="This is a sample video description.",
            thumbnail_url="http://example.com/thumbnail.jpg",
            category="Sample Category"
        )


    def test_get_content_list_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(set(response.data[0].keys()), self.expected_fields)
        self.assertEqual(response.data[0]['title'], self.video.title)
        self.assertEqual(response.data[0]['description'], self.video.description)
        self.assertIn('created_at', response.data[0])


    def test_get_content_list_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)