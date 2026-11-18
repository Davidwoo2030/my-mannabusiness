"""stt.srt → summary.md (Groq 채팅 모델)"""
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
CHUNK_CHARS = 12000  # 긴 영상은 나눠서 요약한 뒤 합친다

SYSTEM = (
    "당신은 유튜브 영상 내용을 정리하는 도우미입니다. 한국어로 답하세요. "
    "마크다운으로 다음 구조를 지키세요: 한 줄 요약, 핵심 포인트(불릿 5~10개), "
    "주요 내용 흐름(시간 순서), 결론 또는 시사점. 자막에 없는 내용은 추가하지 마세요."
)


def srt_to_text(srt: str) -> str:
    """SRT 의 번호와 타임스탬프를 빼고 본문만 남긴다."""
    lines = []
    for line in srt.splitlines():
        line = line.strip()
        if not line or line.isdigit() or "-->" in line:
            continue
        lines.append(line)
    text = " ".join(lines)
    return re.sub(r"\s+", " ", text).strip()


def chunk(text: str, size: int = CHUNK_CHARS) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)] or [""]


def ask(prompt: str) -> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY 가 없습니다. key_page.py 로 먼저 저장하세요.")
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": MODEL,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=300,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Groq 요약 실패 {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def summarize(srt_path: Path, summary_path: Path) -> Path:
    text = srt_to_text(srt_path.read_text(encoding="utf-8"))
    if not text:
        raise RuntimeError("자막 본문이 비어 있습니다.")

    parts = chunk(text)
    if len(parts) == 1:
        result = ask(f"다음 자막을 정리해 주세요.\n\n{parts[0]}")
    else:
        partials = [
            ask(f"다음은 긴 영상의 {i + 1}/{len(parts)} 번째 자막입니다. 핵심 내용을 요약해 주세요.\n\n{p}")
            for i, p in enumerate(parts)
        ]
        joined = "\n\n".join(f"[구간 {i + 1}] {s}" for i, s in enumerate(partials))
        result = ask(f"아래는 한 영상을 구간별로 요약한 내용입니다. 전체를 하나로 정리해 주세요.\n\n{joined}")

    summary_path.write_text(result + "\n", encoding="utf-8")
    print(f"[summarize] {summary_path}")
    return summary_path


if __name__ == "__main__":
    src = Path(sys.argv[1])
    summarize(src, src.with_name("summary.md"))
