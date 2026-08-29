from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {".git", ".github"}
MAX_BYTES = 2_000_000

FORBIDDEN_PATTERNS = [
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"git@github\.com:nz-genesis/genesis-lab(?:\.git)?"),
    re.compile(r"github\.com/nz-genesis/genesis-lab(?:[/?#]|$)"),
]

FORBIDDEN_FILENAMES = {".env", ".env.local", ".env.production", ".env.development"}

violations = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
        continue
    if path.name in FORBIDDEN_FILENAMES or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
        violations.append(f"forbidden file: {path.relative_to(ROOT)}")
        continue
    try:
        if path.stat().st_size > MAX_BYTES:
            continue
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            violations.append(f"forbidden content pattern in: {path.relative_to(ROOT)}")
            break

if violations:
    print("PUBLIC_BOUNDARY_VIOLATION")
    for violation in violations:
        print(violation)
    sys.exit(1)

print("PUBLIC_BOUNDARY_OK")
