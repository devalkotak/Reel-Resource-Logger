import os
import uuid
from dataclasses import dataclass

import yt_dlp


@dataclass
class DownloadedReel:
    video_path: str
    caption: str
    file_id: str


def download_reel(url: str, download_dir: str = "downloads") -> DownloadedReel:
    os.makedirs(download_dir, exist_ok=True)
    file_id = uuid.uuid4().hex
    outtmpl = os.path.join(download_dir, f"{file_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        out_path = ydl.prepare_filename(info)

    if not os.path.exists(out_path):
        raise RuntimeError(f"yt-dlp did not produce output file for {url}")

    caption = info.get("description") or ""
    return DownloadedReel(video_path=out_path, caption=caption, file_id=file_id)


def cleanup_reel_files(download_dir: str, file_id: str) -> None:
    """Remove the downloaded video and any leftover fragments/thumbnails for file_id."""
    for name in os.listdir(download_dir):
        if name.startswith(file_id):
            try:
                os.remove(os.path.join(download_dir, name))
            except OSError:
                pass
