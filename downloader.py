import os
import uuid

import yt_dlp


def download_reel(url: str, download_dir: str = "downloads") -> str:
    os.makedirs(download_dir, exist_ok=True)
    out_path = os.path.join(download_dir, f"{uuid.uuid4().hex}.mp4")

    ydl_opts = {
        "outtmpl": out_path,
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if not os.path.exists(out_path):
        raise RuntimeError(f"yt-dlp did not produce output file for {url}")

    return out_path
