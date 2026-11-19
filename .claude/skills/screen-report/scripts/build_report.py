#!/usr/bin/env python3
"""report.json → PDF 보고서 (한글 지원).

사용 예: build_report.py report.json --out report.pdf
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, ListFlowable, ListItem,
                                PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

# (경로 패턴, TTC 서브폰트 인덱스)
FONT_CANDIDATES = [
    ("C:/Windows/Fonts/malgun.ttf", 0),
    ("C:/Windows/Fonts/malgunbd.ttf", 0),
    ("/System/Library/Fonts/AppleSDGothicNeo.ttc", 0),
    ("/Library/Fonts/NanumGothic.ttf", 0),
    ("~/Library/Fonts/NanumGothic*.ttf", 0),
    ("/usr/share/fonts/**/NanumGothic.ttf", 0),
    ("/usr/share/fonts/**/NotoSansKR-Regular.*tf", 0),
    ("/usr/share/fonts/**/NotoSansCJK-Regular.ttc", 1),  # 1 = KR
    ("/usr/share/fonts/**/NotoSansCJKkr-Regular.otf", 0),
]


def register_font():
    for pattern, sub in FONT_CANDIDATES:
        for path in glob.glob(os.path.expanduser(pattern), recursive=True):
            try:
                pdfmetrics.registerFont(TTFont("KR", path, subfontIndex=sub))
                return "KR", path
            except Exception:
                continue  # CFF 기반 OTF 등은 reportlab이 못 읽음
    # 시스템에 한글 TTF가 없으면 나눔고딕(OFL)을 캐시에 받아 PDF에 내장
    cached = download_font()
    if cached:
        try:
            pdfmetrics.registerFont(TTFont("KR", cached))
            return "KR", cached
        except Exception:
            pass
    # 최후 수단: 내장 CID 글꼴(PDF에 내장되지 않아 일부 뷰어에서 한글이 안 보일 수 있음)
    pdfmetrics.registerFont(UnicodeCIDFont("HYGothic-Medium"))
    return "HYGothic-Medium", "builtin CID (not embedded)"


FONT_URL = ("https://github.com/google/fonts/raw/main/ofl/nanumgothic/"
            "NanumGothic-Regular.ttf")


def download_font():
    cache = os.path.join(os.path.expanduser("~"), ".cache", "screen-report",
                         "NanumGothic-Regular.ttf")
    if os.path.exists(cache) and os.path.getsize(cache) > 100_000:
        return cache
    try:
        import urllib.request
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        tmp = cache + ".part"
        with urllib.request.urlopen(FONT_URL, timeout=30) as r, open(tmp, "wb") as f:
            f.write(r.read())
        os.replace(tmp, cache)
        return cache
    except Exception:
        return None


def styles(font):
    base = dict(fontName=font, leading=16, fontSize=10.5,
                textColor=colors.HexColor("#222222"), wordWrap="CJK")
    return {
        "title": ParagraphStyle("t", **{**base, "fontSize": 22, "leading": 28,
                                        "alignment": TA_CENTER,
                                        "textColor": colors.HexColor("#0b3d91")}),
        "sub": ParagraphStyle("s", **{**base, "fontSize": 11, "alignment": TA_CENTER,
                                      "textColor": colors.HexColor("#666666")}),
        "h": ParagraphStyle("h", **{**base, "fontSize": 14, "leading": 20,
                                    "spaceBefore": 10, "spaceAfter": 6,
                                    "textColor": colors.HexColor("#0b3d91")}),
        "body": ParagraphStyle("b", **{**base, "spaceAfter": 6}),
        "small": ParagraphStyle("sm", **{**base, "fontSize": 8.5, "leading": 12,
                                         "textColor": colors.HexColor("#555555")}),
        "box": ParagraphStyle("bx", **{**base, "fontSize": 11, "leading": 17}),
    }


def p(text, style):
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def bullets(items, st):
    return ListFlowable([ListItem(p(i, st["body"]), leftIndent=12) for i in items],
                        bulletType="bullet", start="•", leftIndent=12,
                        bulletFontName=st["body"].fontName)


def heading(text, st):
    return [p(text, st["h"]),
            Table([[""]], colWidths=["100%"], rowHeights=[1],
                  style=[("LINEABOVE", (0, 0), (-1, -1), 0.8,
                          colors.HexColor("#0b3d91"))])]


def screenshot_flow(path, max_w, max_h):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return Image(path, width=w * scale, height=h * scale)


def build(data, out, font):
    st = styles(font)
    page_w, page_h = A4
    margin = 18 * mm
    avail_w = page_w - 2 * margin
    story = []

    story += [Spacer(1, 10 * mm), p(data.get("title", "화면 분석 보고서"), st["title"]),
              Spacer(1, 3 * mm)]
    sub = data.get("subtitle") or dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    story += [p(sub, st["sub"]), Spacer(1, 8 * mm)]

    if data.get("summary"):
        box = Table([[p(data["summary"], st["box"])]], colWidths=[avail_w])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef3fb")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#0b3d91")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story += [p("핵심 요약", st["h"]), box, Spacer(1, 6 * mm)]

    shot = data.get("screenshot")
    if shot and os.path.exists(os.path.expanduser(shot)):
        img = screenshot_flow(os.path.expanduser(shot), avail_w, page_h * 0.42)
        story += [KeepTogether([p("캡처 화면", st["h"]), img,
                                p("그림 1. 캡처한 모니터 화면", st["small"])])]
    elif shot:
        story += [p(f"(스크린샷 파일을 찾을 수 없음: {shot})", st["small"])]

    if data.get("screen_analysis"):
        story += heading("화면 내용 분석", st) + [bullets(data["screen_analysis"], st)]

    for sec in data.get("sections", []):
        story += heading(sec.get("heading", ""), st)
        if sec.get("body"):
            for para in str(sec["body"]).split("\n\n"):
                story.append(p(para, st["body"]))
        if sec.get("bullets"):
            story.append(bullets(sec["bullets"], st))

    if data.get("insights"):
        story += heading("시사점 및 제안", st) + [bullets(data["insights"], st)]

    if data.get("sources"):
        story += heading("참고 출처", st)
        for i, s in enumerate(data["sources"], 1):
            title = escape(str(s.get("title", s.get("url", ""))))
            url = escape(str(s.get("url", "")))
            story.append(Paragraph(
                f'[{i}] {title}<br/><link href="{url}" color="#1a55c4">{url}</link>',
                st["small"]))
            story.append(Spacer(1, 2 * mm))

    created = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(font, 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(margin, 10 * mm, f"자동 생성 화면 보고서 · {created}")
        canvas.drawRightString(page_w - margin, 10 * mm, f"{doc.page}")
        canvas.restoreState()

    out = os.path.abspath(os.path.expanduser(out))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=margin, rightMargin=margin,
                            topMargin=margin, bottomMargin=18 * mm,
                            title=data.get("title", "화면 분석 보고서"),
                            author="screen-report")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--out")
    a = ap.parse_args()
    with open(a.json_path, encoding="utf-8") as f:
        data = json.load(f)
    out = a.out or os.path.join(
        os.path.expanduser("~/Documents/ScreenReports"),
        dt.datetime.now().strftime("screen-report_%Y%m%d_%H%M%S.pdf"))
    font, font_src = register_font()
    path = build(data, out, font)
    print(json.dumps({"ok": True, "pdf": path, "font": font_src}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"},
                         ensure_ascii=False))
        sys.exit(1)
