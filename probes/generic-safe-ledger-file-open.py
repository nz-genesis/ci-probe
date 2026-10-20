#!/usr/bin/env python3
"""Generic public probe: safely opening a local state file under hostile path types.

This probe is implementation-agnostic and contains no private product code.
It establishes only the behavior of this generic file-opening primitive.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def read_regular_file(path: Path) -> bytes | None:
    """Read a regular file without following its final symlink or blocking on FIFO."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise RuntimeError("required no-follow/nonblocking open flags are unavailable")
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise RuntimeError("cannot safely open state file") from exc

    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise RuntimeError("state path must be a regular file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(descriptor)


class SafeFileOpenProbe(unittest.TestCase):
    def test_regular_file_is_read_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state"
            path.write_bytes(b"synthetic-state\n")
            self.assertEqual(read_regular_file(path), b"synthetic-state\n")

    def test_missing_file_is_reported_as_absent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(read_regular_file(Path(directory) / "absent"))

    @unittest.skipUnless(
        hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_NONBLOCK") and hasattr(os, "mkfifo"),
        "requires POSIX no-follow/nonblocking open and FIFO support",
    )
    def test_fifo_is_rejected_in_bounded_child_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state"
            os.mkfifo(path)
            completed = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--child-open", str(path)],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(
                completed.stdout.startswith("REJECTED:state path must be a regular file"),
                completed.stdout,
            )
            self.assertTrue(path.is_fifo())

    @unittest.skipUnless(
        hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_NONBLOCK"),
        "requires POSIX no-follow/nonblocking open support",
    )
    def test_symlink_is_rejected_without_changing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "sentinel"
            link = root / "state"
            original = b"sentinel-must-remain-unchanged\n"
            target.write_bytes(original)
            link.symlink_to(target)
            with self.assertRaisesRegex(RuntimeError, "cannot safely open state file"):
                read_regular_file(link)
            self.assertTrue(link.is_symlink())
            self.assertEqual(target.read_bytes(), original)


def _child_open(path: Path) -> int:
    try:
        read_regular_file(path)
    except RuntimeError as exc:
        print(f"REJECTED:{exc}")
        return 0
    print("UNEXPECTED_SUCCESS")
    return 7


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--child-open":
        raise SystemExit(_child_open(Path(sys.argv[2])))
    unittest.main(verbosity=2)
