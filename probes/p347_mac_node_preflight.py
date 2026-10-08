#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
from datetime import datetime, timezone

def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()

record = {
    "probe": "P347_MAC_NODE_PREFLIGHT",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "hostname": socket.gethostname(),
    "platform": platform.platform(),
    "machine": platform.machine(),
    "python": platform.python_version(),
    "runner_name": os.environ.get("RUNNER_NAME", ""),
    "runner_os": os.environ.get("RUNNER_OS", ""),
    "runner_arch": os.environ.get("RUNNER_ARCH", ""),
    "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
    "github_sha": os.environ.get("GITHUB_SHA", ""),
    "github_ref": os.environ.get("GITHUB_REF", ""),
    "git_checked_out_sha": run("git", "rev-parse", "HEAD"),
    "security_boundary": {
        "trusted_push_only": True,
        "pull_request_triggers": False,
        "purpose": "bounded P347 execution substrate",
    },
}

for command, key in [
    (("sw_vers", "-productVersion"), "macos_version"),
    (("uname", "-a"), "uname"),
]:
    try:
        record[key] = run(*command)
    except Exception as exc:
        record[key] = f"ERROR:{type(exc).__name__}"

print(json.dumps(record, indent=2, sort_keys=True))
with open("p347-mac-node-preflight.json", "w", encoding="utf-8") as fh:
    json.dump(record, fh, indent=2, sort_keys=True)
    fh.write("\n")
