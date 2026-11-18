"""audio.mp3 → stt.srt (Groq whisper-large-v3, SRT 형식)"""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MODEL = "whisper-large-v3"
MAX_BYTES = 25 * 1024 * 1024  # Groq 무료 플랜 업로드 한도


def transcribe(audio_path: Path, srt_path: Path) -> Path:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY 가 없습니다. key_page.py 로 먼저 저장하세요.")
    size = audio_path.stat().st_size
    if size > MAX_BYTES:
        raise RuntimeError(f"파일이 {size / 1048576:.1f}MB 로 Groq 한도(25MB)를 넘습니다.")

    with audio_path.open("rb") as f:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {key}"},
            files={"file": (audio_path.name, f, "audio/mpeg")},
            data={"model": MODEL, "response_format": "srt", "temperature": "0"},
            timeout=600,
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Groq 전사 실패 {resp.status_code}: {resp.text[:300]}")

    srt_path.write_text(resp.text, encoding="utf-8")
    print(f"[transcribe] {srt_path}")
    return srt_path


if __name__ == "__main__":
    src = Path(sys.argv[1])
    transcribe(src, src.with_name("stt.srt"))
