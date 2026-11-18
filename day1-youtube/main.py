"""유튜브 주소 하나로 다운로드 → 전사 → 요약을 차례로 실행.

사용법: python main.py "https://www.youtube.com/watch?v=..." [--force]
--force: 이미 있는 결과 파일도 다시 만든다.
"""
import argparse
import sys
from pathlib import Path

from download_audio import download_audio
from summarize import summarize
from transcribe import transcribe


def main() -> int:
    parser = argparse.ArgumentParser(description="유튜브 → 오디오 → 자막 → 요약")
    parser.add_argument("url")
    parser.add_argument("--force", action="store_true", help="기존 결과를 무시하고 다시 실행")
    args = parser.parse_args()

    try:
        video_id, audio = download_audio(args.url)
        out_dir: Path = audio.parent
        srt = out_dir / "stt.srt"
        md = out_dir / "summary.md"

        if args.force or not srt.exists():
            transcribe(audio, srt)
        else:
            print(f"[skip] 자막 있음: {srt}")

        if args.force or not md.exists():
            summarize(srt, md)
        else:
            print(f"[skip] 요약 있음: {md}")

        print(f"\n완료: {out_dir}")
        return 0
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
