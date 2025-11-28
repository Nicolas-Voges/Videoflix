from .models import Video
from .utils import generate_hls_files


def transcode_video(video_id):
    """
    Transcode a video to HLS format and update its processing status.

    This function is intended to run as a background task using RQ.

    Raises:
        Exception: Any exception raised during HLS generation is propagated.
    """
    video = Video.objects.get(id=video_id)
    video.status = "processing"
    video.save()

    try:
        generate_hls_files(video.original_file.path, video.id)

        video.status = "ready"
        video.save()

    except Exception as error:
        video.status = "failed"
        video.save()
        raise error