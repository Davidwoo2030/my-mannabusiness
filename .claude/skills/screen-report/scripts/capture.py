#!/usr/bin/env python3
"""모니터 목록 조회 및 지정 모니터 캡처.

사용 예:
  capture.py --list
  capture.py --monitor 2 --out screen.png [--crop x,y,w,h] [--max-width 1600]
결과는 JSON으로 stdout에 출력한다.
"""
import argparse
import json
import os
import sys


def fail(msg, code=1):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.exit(code)


def _mss_ctor(mss):
    return getattr(mss, "MSS", None) or mss.mss


def list_monitors():
    try:
        import mss
    except ImportError:
        fail("mss 모듈이 없습니다: python3 -m pip install mss pillow")
    try:
        with _mss_ctor(mss)() as sct:
            mons = sct.monitors
    except Exception as e:  # 디스플레이 없음 등
        fail(f"화면에 접근할 수 없습니다(디스플레이 없음?): {e}")
    out = []
    for i, m in enumerate(mons):
        out.append({
            "index": i,
            "label": "전체(모든 모니터)" if i == 0 else f"모니터 {i}" + (" (주)" if i == 1 else ""),
            "left": m["left"], "top": m["top"],
            "width": m["width"], "height": m["height"],
        })
    return out


def capture(index, out_path, crop=None, max_width=1600):
    import mss
    from PIL import Image

    mons = list_monitors()
    if index < 0 or index >= len(mons):
        fail(f"모니터 {index}이(가) 없습니다. 사용 가능: "
             + ", ".join(str(m["index"]) for m in mons))
    with _mss_ctor(mss)() as sct:
        mon = sct.monitors[index]
        region = dict(mon)
        if crop:
            x, y, w, h = crop
            region = {"left": mon["left"] + x, "top": mon["top"] + y,
                      "width": w, "height": h}
        shot = sct.grab(region)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

    out_path = os.path.abspath(os.path.expanduser(out_path))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")

    # 분석용 축소본 (이미지 읽기 비용 절감)
    base, _ = os.path.splitext(out_path)
    analysis_path = base + "_analysis.jpg"
    small = img.copy()
    if small.width > max_width:
        small.thumbnail((max_width, max_width * 10))
    small.save(analysis_path, "JPEG", quality=85)

    return {"ok": True, "monitor": index, "path": out_path,
            "analysis_path": analysis_path,
            "width": img.width, "height": img.height}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--monitor", type=int, default=1)
    ap.add_argument("--out", default="screen.png")
    ap.add_argument("--crop", help="x,y,w,h (모니터 기준 좌표)")
    ap.add_argument("--max-width", type=int, default=1600)
    a = ap.parse_args()

    if a.list:
        print(json.dumps({"ok": True, "monitors": list_monitors()},
                         ensure_ascii=False, indent=2))
        return
    crop = None
    if a.crop:
        try:
            crop = [int(v) for v in a.crop.split(",")]
            assert len(crop) == 4
        except Exception:
            fail("--crop 형식은 x,y,w,h 입니다")
    print(json.dumps(capture(a.monitor, a.out, crop, a.max_width),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
