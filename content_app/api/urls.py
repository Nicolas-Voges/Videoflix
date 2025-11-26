from django.urls import path

from .views import VideoListAPIView, video_playlist_view

urlpatterns = [
    path('video/', VideoListAPIView.as_view(), name="video-list"),
    path('api/video/<int:movie_id>/<str:resolution>/index.m3u8', video_playlist_view, name='video-playlist'),
]