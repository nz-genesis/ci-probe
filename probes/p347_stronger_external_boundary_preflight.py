#!/usr/bin/env python3
"""P347+ public execution-surface preflight.

Public-run trigger revision: v0.1.

This probe proves only that a public CI run can expose independent runner
identity and the local capabilities needed by the stronger experiment. It
must never be interpreted as external-authority or packet-witness evidence.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

def identity() -> dict[str, str | None]:
    return {
        "hostname": socket.gethostname(),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "job": os.environ.get("GITHUB_JOB"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "sha": os.environ.get("GITHUB_SHA"),
    }

def capability(name: str) -> bool:
    return shutil.which(name) is not None

def main() -> int:
    result = {
        "probe": "P347_STRONGER_EXTERNAL_BOUNDARY_PREFLIGHT",
        "status": "PRECHECK",
        "identity": identity(),
        "capabilities": {
            "python3": capability("python3"),
            "tcpdump": capability("tcpdump"),
            "curl": capability("curl"),
            "iptables": capability("iptables"),
            "ip6tables": capability("ip6tables"),
        },
        "external_authority_configured": bool(os.environ.get("P347_EXTERNAL_AUTHORITY_URL")),
        "network_witness_configured": bool(os.environ.get("P347_NETWORK_WITNESS_ID")),
        "evidence_boundary": (
            "Public CI execution surface only. This result is not evidence of "
            "external authority independence, packet-level witnessing, physical "
            "effect, or lost-ACK reconciliation."
        ),
    }
    Path("p347-stronger-preflight.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    missing = [
        k for k, v in result["capabilities"].items()
        if not v
    ]
    if missing:
        print("P347_STRONGER_PREFLIGHT=BLOCKED")
        print("Missing local capabilities:", ", ".join(missing))
        return 2
    if not result["external_authority_configured"]:
        print("P347_STRONGER_EXTERNAL_AUTHORITY=NOT_CONFIGURED")
    if not result["network_witness_configured"]:
        print("P347_STRONGER_NETWORK_WITNESS=NOT_CONFIGURED")
    print("P347_STRONGER_PUBLIC_EXECUTION_SURFACE=READY")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
