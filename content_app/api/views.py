from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from content_app.models import Video
from content_app.api.serializers import VideoListSerializer


class VideoListAPIView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]