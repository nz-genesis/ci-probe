from pathlib import Path
import platform
import subprocess
import sys

EXPECTED = "CI_PROBE_OK"
TEST_MARKER = "P347_N100_WITNESS_CONTRACT_TESTS=PASS"

print(f"python={platform.python_version()}")
print(f"platform={platform.platform()}")

# Run real filesystem/pure-contract tests for the N100 capture apparatus.
# These tests do not claim physical topology or packet-witness evidence.
subprocess.run(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "p347/n100-witness",
        "-p",
        "test_*.py",
        "-v",
    ],
    check=True,
)
print(TEST_MARKER)
print(EXPECTED)

Path("ci-probe-result.txt").write_text(
    f"{EXPECTED}\npython={sys.version}\nplatform={platform.platform()}\n{TEST_MARKER}\n",
    encoding="utf-8",
)
