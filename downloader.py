import os
import uuid

import yt_dlp


def download_reel(url: str, download_dir: str = "downloads") -> str:
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

    return out_path
