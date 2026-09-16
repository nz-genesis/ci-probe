import json
import os
import shutil
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

candidate = os.environ.get("BROWSER_CANDIDATE")
if candidate not in {"playwright-python", "patchright-python"}:
    raise SystemExit(f"Unsupported candidate: {candidate}")

if candidate == "playwright-python":
    from playwright.sync_api import sync_playwright
else:
    from patchright.sync_api import sync_playwright

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/echo"):
            from urllib.parse import parse_qs, urlparse
            request_id = parse_qs(urlparse(self.path).query).get("request_id", [None])[0]
            body = json.dumps({"request_id": request_id, "observed": True}).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return
        body = b'''<!doctype html><button id="action">Run request</button><output id="state">0</output><script>
        document.querySelector('#action').addEventListener('click', async () => {
          const id = crypto.randomUUID(); const r = await fetch('/api/echo?request_id=' + id); const j = await r.json();
          localStorage.setItem('request_id', j.request_id); document.querySelector('#state').textContent = j.observed ? '1' : '0';
        });</script>'''
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *_):
        pass

root = Path(tempfile.mkdtemp(prefix="web2api-runtime-"))
profile_a, profile_b = root / "profile-a", root / "profile-b"
server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_address[1]}"
result = {"candidate": candidate, "checks": {}, "timings_ms": {}, "rss_mb": None}
try:
    with sync_playwright() as p:
        t = time.perf_counter()
        context = p.chromium.launch_persistent_context(str(profile_a), headless=True)
        result["timings_ms"]["first_launch"] = (time.perf_counter() - t) * 1000
        page = context.new_page()
        page.goto(base)
        page.get_by_role("button", name="Run request").click()
        page.locator("#state").wait_for(state="visible")
        request_id = page.evaluate("localStorage.getItem('request_id')")
        result["checks"]["semantic_interaction"] = page.locator("#state").text_content() == "1"
        result["checks"]["request_correlation"] = isinstance(request_id, str) and len(request_id) >= 16
        timed_out = False
        try:
            page.locator("#never-exists").wait_for(state="visible", timeout=100)
        except Exception:
            timed_out = True
        result["checks"]["timeout_detection"] = timed_out
        context.close()

        t = time.perf_counter()
        context = p.chromium.launch_persistent_context(str(profile_a), headless=True)
        result["timings_ms"]["restart"] = (time.perf_counter() - t) * 1000
        page = context.new_page()
        page.goto(base)
        result["checks"]["persistence"] = bool(page.evaluate("localStorage.getItem('request_id')"))
        context.close()

        context = p.chromium.launch_persistent_context(str(profile_b), headless=True)
        page = context.new_page()
        page.goto(base)
        result["checks"]["profile_isolation"] = not bool(page.evaluate("localStorage.getItem('request_id')"))
        context.close()

        context = p.chromium.launch_persistent_context(str(profile_a), headless=True)
        disconnected_page = context.new_page()
        disconnected_page.goto(base)
        context.close()
        disconnected = False
        try:
            disconnected_page.title()
        except Exception:
            disconnected = True
        result["checks"]["closed_browser_detection"] = disconnected

    result["checks"]["all_pass"] = all(result["checks"].values())
    print(json.dumps(result, indent=2))
    if not result["checks"]["all_pass"]:
        raise SystemExit(1)
finally:
    server.shutdown()
    server.server_close()
    shutil.rmtree(root, ignore_errors=True)
