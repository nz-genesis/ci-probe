from pathlib import Path
import platform
import sys

EXPECTED = "CI_PROBE_OK"

print(EXPECTED)
print(f"python={platform.python_version()}")
print(f"platform={platform.platform()}")

Path("ci-probe-result.txt").write_text(
    f"{EXPECTED}\npython={sys.version}\nplatform={platform.platform()}\n",
    encoding="utf-8",
)
