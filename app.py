import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from splice import Splice

box = Splice()

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, kind="application/json"):
        raw = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, json.dumps({"ok": True}))
            return
        if self.path == "/records":
            self._send(200, json.dumps({"records": [{"seq": s, "body": b} for s, b in box.take()]}))
            return
        if self.path == "/":
            self._send(200, "<!doctype html><title>日志</title><pre id=out></pre><script>fetch('/records').then(r=>r.json()).then(j=>{out.textContent=JSON.stringify(j)})</script>", "text/html")
            return
        self._send(404, json.dumps({"ok": False}))

    def do_POST(self):
        if self.path != "/ingest":
            self._send(404, json.dumps({"ok": False}))
            return
        n = int(self.headers.get("Content-Length") or 0)
        box.feed(self.rfile.read(n))
        self._send(200, json.dumps({"ok": True}))

    def log_message(self, fmt, *args):
        return

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8765"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
