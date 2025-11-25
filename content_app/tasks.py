from .models import Video
from .utils import generate_hls_files


def transcode_video(video_id):
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