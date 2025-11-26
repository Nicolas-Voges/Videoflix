from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from content_app.models import Video
from content_app.tasks import transcode_video

User = get_user_model()

class VideoListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Test123$', email='testuser@example.com')
        self.url = reverse('video-list')
        self.login_url = reverse('login')
        self.expected_fields = {'id', 'created_at', 'title', 'description', 'thumbnail_url', 'category'}
        self.video = Video.objects.create(
            title="Sample Video",
            description="This is a sample video description.",
            thumbnail_url="http://example.com/thumbnail.jpg",
            category="Sample Category",
            original_file="videos/originals/test.mp4",
            status="pending"
        )


    def test_get_content_list_success(self):
        self.client.post(self.login_url, data={'email': 'testuser@example.com', 'password': 'Test123$'})
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


class VideoUploadTests(TestCase):

    @patch("content_app.signals.django_rq.get_queue")  
    def test_admin_upload_triggers_transcoding(self, mock_job):
        mock_queue = mock_job.return_value
        fake_video = SimpleUploadedFile(
            name="test.mp4",
            content=b"\x00" * 1024,
            content_type="video/mp4"
        )

        video = Video.objects.create(
            title="Test Video",
            description="Test description",
            thumbnail_url="https://example.com/thumb.jpg",
            category="Test",
            original_file=fake_video,
        )

        self.assertIsNotNone(video.id)
        mock_queue.enqueue.assert_called_once_with(transcode_video, video.id)
        self.assertIn("test", video.original_file.name)
        self.assertTrue(video.original_file.name.endswith(".mp4"))