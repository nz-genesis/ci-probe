"""Run the full scenario-matrix unittest suite."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(ROOT / "action_probe"),
        pattern="test_*.py",
        top_level_dir=str(ROOT),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("EXECUTION_SCENARIO_MATRIX_OK")


if __name__ == "__main__":
    main()
