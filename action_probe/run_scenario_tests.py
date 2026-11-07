"""Run root action-contract tests and the complete scenario-matrix suite."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = Path(__file__).resolve().parent
for path in (str(ROOT), str(PROBE_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)


def main():
    loader = unittest.defaultTestLoader
    root_suite = loader.discover(
        start_dir=str(ROOT),
        pattern="test_action_probe.py",
        top_level_dir=str(ROOT),
    )
    scenario_suite = loader.discover(
        start_dir=str(PROBE_DIR),
        pattern="test_*.py",
        top_level_dir=str(PROBE_DIR),
    )
    suite = unittest.TestSuite((root_suite, scenario_suite))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("GENERIC_ACTION_AND_SCENARIO_TESTS_OK")


if __name__ == "__main__":
    main()
