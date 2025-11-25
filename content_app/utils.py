import subprocess
from pathlib import Path
from django.conf import settings

RESOLUTIONS = {
    "120p": "214x120",
    "360p": "640x360",
    "720p": "1280x720",
    "1080p": "1920x1080",
}


def generate_hls_files(input_path: str, video_id: int):

    output_root = Path(settings.MEDIA_ROOT) / f"videos/{video_id}/"
    output_root.mkdir(parents=True, exist_ok=True)

    master_playlist_content = []

    for label, size in RESOLUTIONS.items():
        out_dir = output_root / label
        out_dir.mkdir(exist_ok=True)

        playlist_path = out_dir / "index.m3u8"

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale={size}",
            "-preset", "veryfast",
            "-g", "48",
            "-hls_time", "3",
            "-hls_playlist_type", "vod",
            str(playlist_path),
        ]

        subprocess.run(cmd, check=True)

        master_playlist_content.append(
            f"#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION={size}\n{label}/index.m3u8"
        )

    master_playlist = output_root / "index.m3u8"
    master_playlist.write_text("#EXTM3U\n" + "\n".join(master_playlist_content))