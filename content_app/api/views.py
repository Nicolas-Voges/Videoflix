from pathlib import Path

from django.http import FileResponse, Http404
from django.conf import settings

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from content_app.models import Video
from content_app.api.serializers import VideoListSerializer

class VideoListAPIView(ListAPIView):
    """
    API view to list all videos.

    Returns a list of video objects serialized with VideoListSerializer.
    Access is restricted to authenticated users.
    """

    queryset = Video.objects.all()
    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]


def video_playlist_view(request, movie_id: int, resolution: str):
    """
    Serve the HLS playlist (.m3u8) for a given video and resolution.

    Raises:
        Http404: If the playlist file does not exist.

    Returns:
        FileResponse: Returns the playlist file with content type 'application/vnd.apple.mpegurl'.
    """

    playlist_path = Path(settings.MEDIA_ROOT) / f"videos/{movie_id}/{resolution}/index.m3u8"
    if not playlist_path.exists():
        raise Http404("Playlist not found")

    return FileResponse(open(playlist_path, "rb"), content_type="application/vnd.apple.mpegurl")


def video_segment_view(request, movie_id: int, resolution: str, segment: str):
    """
    Serve a video segment (.ts) for HLS streaming.

    Raises:
        Http404: If the segment file does not exist.

    Returns:
        FileResponse: Returns the video segment file with content type 'video/mp2t'.
    """
    segment_path = Path(settings.MEDIA_ROOT) / f"videos/{movie_id}/{resolution}/{segment}"
    if not segment_path.exists():
        raise Http404("Segment not found")

    return FileResponse(open(segment_path, "rb"), content_type="video/mp2t")