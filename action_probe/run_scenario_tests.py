"""Run the full scenario-matrix unittest suite without shadowing root action_probe.py."""
from pathlib import Path
import sys
import unittest

PROBE_DIR = Path(__file__).resolve().parent
if str(PROBE_DIR) not in sys.path:
    sys.path.insert(0, str(PROBE_DIR))


def main():
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(PROBE_DIR),
        pattern="test_*.py",
        top_level_dir=str(PROBE_DIR),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("EXECUTION_SCENARIO_MATRIX_OK")


if __name__ == "__main__":
    main()
