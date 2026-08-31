import os
import subprocess

expected = os.environ["GITHUB_SHA"]
actual = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
assert actual == expected, f"checkout SHA mismatch: {actual} != {expected}"
print(f"PASS24 execution smoke: repository={os.environ.get('GITHUB_REPOSITORY')} sha={actual}")
