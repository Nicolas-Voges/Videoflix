import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
from .tasks import transcode_video


@receiver(post_save, sender=Video)
def start_transcoding_job(sender, instance, created, *args, **kwargs):
    """
    Trigger a background transcoding job when a new Video instance is created.

    This signal listens to the post_save event of the Video model.
    If a new video is created, it enqueues the `transcode_video` task
    in the default RQ queue with the video's ID.
    """
    
    if created:
        queue = django_rq.get_queue("default")
        queue.enqueue(transcode_video, instance.id)