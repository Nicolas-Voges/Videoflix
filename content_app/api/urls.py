from django.urls import path

from .views import VideoListAPIView, video_playlist_view, video_segment_view

urlpatterns = [
    path('video/', VideoListAPIView.as_view(), name="video-list"),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', video_playlist_view, name='video-playlist'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', video_segment_view, name='video-segment')
]