from pathlib import Path

from django.http import FileResponse, Http404
from django.conf import settings

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from content_app.models import Video
from content_app.api.serializers import VideoListSerializer

class VideoListAPIView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]


def video_playlist_view(request, movie_id: int, resolution: str):
    playlist_path = Path(settings.MEDIA_ROOT) / f"videos/{movie_id}/{resolution}/index.m3u8"
    if not playlist_path.exists():
        raise Http404("Playlist not found")

    return FileResponse(open(playlist_path, "rb"), content_type="application/vnd.apple.mpegurl")