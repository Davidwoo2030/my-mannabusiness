"""키를 .env 에 저장하는 로컬 웹 페이지.

실행: python key_page.py  →  http://127.0.0.1:8765 에서 GROQ_API_KEY 입력
키는 채팅/로그에 남지 않고 .env 파일에만 저장된다.
"""
import html
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from dotenv import dotenv_values

ENV_PATH = Path(__file__).resolve().parent / ".env"
HOST, PORT = "127.0.0.1", 8765


def save_key(key: str) -> None:
    lines = []
    if ENV_PATH.exists():
        lines = [l for l in ENV_PATH.read_text(encoding="utf-8").splitlines()
                 if not l.startswith("GROQ_API_KEY=")]
    lines.append(f"GROQ_API_KEY={key}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def key_status() -> str:
    key = dotenv_values(ENV_PATH).get("GROQ_API_KEY") if ENV_PATH.exists() else None
    if not key:
        return "저장된 키가 없습니다."
    return f"저장된 키: {key[:6]}…{key[-4:]} (길이 {len(key)})"


PAGE = """<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Groq 키 저장</title>
<body style="font-family:system-ui;max-width:520px;margin:40px auto;padding:0 16px">
<h2>Groq API 키 저장</h2>
<p>{status}</p>
<form method="post" action="/">
<input name="key" type="password" placeholder="gsk_..." required
 style="width:100%;padding:10px;font:inherit;box-sizing:border-box">
<p><button type="submit" style="padding:10px 16px;font:inherit">.env 에 저장</button></p>
</form>
<p style="color:#666;font-size:14px">저장 위치: {path}</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: str, code: int = 200) -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _page(self, status: str) -> str:
        return PAGE.format(status=html.escape(status), path=html.escape(str(ENV_PATH)))

    def do_GET(self):
        self._send(self._page(key_status()))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        key = form.get("key", [""])[0].strip()
        if not re.fullmatch(r"gsk_[A-Za-z0-9]+", key):
            self._send(self._page("형식이 맞지 않습니다. Groq 키는 gsk_ 로 시작합니다."), 400)
            return
        save_key(key)
        self._send(self._page("저장했습니다. " + key_status()))

    def log_message(self, fmt, *args):  # 키가 로그에 찍히지 않도록 접근 로그 끔
        pass


if __name__ == "__main__":
    print(f"http://{HOST}:{PORT} 에서 키를 입력하세요. 종료: Ctrl+C")
    HTTPServer((HOST, PORT), Handler).serve_forever()
