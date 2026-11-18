"""유튜브 주소 → downloads/{video_id}/audio.mp3"""
from pathlib import Path

import yt_dlp

BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS = BASE_DIR / "downloads"


def download_audio(url: str) -> tuple[str, Path]:
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    video_id = info["id"]
    out_dir = DOWNLOADS / video_id
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = out_dir / "audio.mp3"

    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_dir / "audio.%(ext)s"),
        "overwrites": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "64",  # 용량을 줄여 Groq 업로드 한도에 여유를 둔다
        }],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    if not mp3_path.exists():
        raise RuntimeError(f"audio.mp3 생성 실패: {mp3_path}")
    print(f"[download] {mp3_path}")
    return video_id, mp3_path


if __name__ == "__main__":
    import sys
    download_audio(sys.argv[1])
