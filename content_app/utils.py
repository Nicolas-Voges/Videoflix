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
    """
    Generate HLS (HTTP Live Streaming) playlist and video segments for a given video.

    This function uses ffmpeg to transcode the input video into multiple resolutions
    and creates both the individual resolution playlists and a master playlist.

    Args:
        input_path (str): Path to the original video file.
        video_id (int): ID of the Video instance, used to create output directories.

    Steps:
        1. Create output directories for each resolution.
        2. Transcode the video into .ts segments for HLS using ffmpeg.
        3. Generate an index.m3u8 playlist for each resolution.
        4. Create a master playlist referencing all resolution playlists.

    Raises:
        subprocess.CalledProcessError: If ffmpeg fails during transcoding.
    """

    # Create directory for this resolution
    output_root = Path(settings.MEDIA_ROOT) / f"videos/{video_id}/"
    output_root.mkdir(parents=True, exist_ok=True)

    master_playlist_content = []

    for label, size in RESOLUTIONS.items():
        out_dir = output_root / label
        out_dir.mkdir(exist_ok=True)

        # Path to the resolution-specific playlist
        playlist_path = out_dir / "index.m3u8"

        # ffmpeg command to transcode video into HLS segments
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

        # Run ffmpeg and raise error if it fails
        subprocess.run(cmd, check=True)

        # Add entry to the master playlist
        master_playlist_content.append(
            f"#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION={size}\n{label}/index.m3u8"
        )

    # Write master playlist referencing all resolutions
    master_playlist = output_root / "index.m3u8"
    master_playlist.write_text("#EXTM3U\n" + "\n".join(master_playlist_content))