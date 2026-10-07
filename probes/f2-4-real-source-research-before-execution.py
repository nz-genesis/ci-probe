#!/usr/bin/env python3
"""Public-safe generic control for F2.4 real-source research-before-execution.

Genesis semantics/private source are intentionally excluded. The control proves
only the generic property: real external source -> observed evidence -> derived
candidate -> freshness revalidation -> real read-only execution -> artifact.
"""
from __future__ import annotations

import hashlib
import json
import http.server
import re
import threading
import urllib.request
from pathlib import Path

SOURCE_URL = "https://www.rfc-editor.org/rfc/rfc9110.txt"
ACTION_URL = SOURCE_URL
SAFE_METHODS_RE = re.compile(
    r"the\s+([A-Z]+(?:,\s*[A-Z]+)*(?:,?\s+and\s+[A-Z]+))\s+methods?"
    r"\s+are\s+defined\s+to\s+be\s+safe",
    re.IGNORECASE,
)


def fetch(url: str) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Genesis-F2.4-Public-Control/1.0"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=20.0) as response:
        body = response.read().decode("utf-8")
        if response.status != 200:
            raise AssertionError(f"unexpected HTTP status: {response.status}")
    return body, hashlib.sha256(body.encode("utf-8")).hexdigest()


class MutableHandler(http.server.BaseHTTPRequestHandler):
    body = b"the GET method is defined to be safe.\\n"

    def do_GET(self):
        payload = self.body
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def run_stale_source_adversarial_case() -> dict:
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), MutableHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/source"
        first_body, first_sha = fetch(url)
        assert "GET" in first_body
        MutableHandler.body = b"the POST method is defined to be safe.\\n"
        second_body, second_sha = fetch(url)
        assert second_body != first_body
        assert second_sha != first_sha
        execution_allowed = second_sha == first_sha
        assert execution_allowed is False
        return {
            "status": "PASS",
            "property": "stale research is rejected before execution",
            "research_sha256": first_sha,
            "current_sha256": second_sha,
            "execution_allowed": execution_allowed,
        }
    finally:
        MutableHandler.body = b"the GET method is defined to be safe.\\n"
        server.shutdown()


def main() -> None:
    first_body, first_sha = fetch(SOURCE_URL)
    match = SAFE_METHODS_RE.search(first_body)
    assert match, "safe-method declaration not found in real source"

    raw = re.sub(r"\s+and\s+", ",", match.group(1), flags=re.IGNORECASE)
    methods = tuple(item.strip().upper() for item in raw.split(",") if item.strip())
    assert methods, "no candidates derived from source"
    assert "GET" in methods

    candidates = [
        {"method": method, "source_sha256": first_sha}
        for method in methods
    ]
    selected = [candidate for candidate in candidates if candidate["method"] == "GET"]
    assert len(selected) == 1

    second_body, second_sha = fetch(SOURCE_URL)
    assert second_sha == first_sha, "source changed before execution"

    action_body, action_sha = fetch(ACTION_URL)
    assert action_body == second_body
    assert action_sha == second_sha

    output = Path("f24-real-source-result.txt")
    output.write_bytes(action_body.encode("utf-8"))
    artifact_sha = hashlib.sha256(output.read_bytes()).hexdigest()
    assert artifact_sha == action_sha

    stale_case = run_stale_source_adversarial_case()

    receipt = {
        "control_id": "F2.4-REAL-SOURCE-RESEARCH-BEFORE-EXECUTION-V1",
        "genesis_semantics_included": False,
        "private_source_included": False,
        "source_url": SOURCE_URL,
        "source_sha256": first_sha,
        "derived_candidates": candidates,
        "selected_candidate": selected[0],
        "revalidated_sha256": second_sha,
        "action_url": ACTION_URL,
        "action_status": 200,
        "artifact_sha256": artifact_sha,
        "stale_source_adversarial_case": stale_case,
    }
    Path("f24-real-source-control-result.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2))
    print("F2_4_REAL_SOURCE_RESEARCH_BEFORE_EXECUTION: PASS")


if __name__ == "__main__":
    main()
