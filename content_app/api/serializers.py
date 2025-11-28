from rest_framework import serializers
from content_app.models import Video

class VideoListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing video objects.

    Returns essential fields such as ID, creation date, title,
    description, thumbnail URL, and category.
    """
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']