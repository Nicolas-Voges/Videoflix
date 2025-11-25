from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video
from .tasks import transcode_video


@receiver(post_save, sender=Video)
def start_transcoding_job(sender, instance, created, *args, **kwargs):
    if created:
        # Create queue job to process video (e.g., generate thumbnails, transcode)
        transcode_video.delay(instance.id)