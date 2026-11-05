#!/usr/bin/env python3
"""Generic POSIX atomic file-publication probe; no private application semantics."""
from __future__ import annotations

import concurrent.futures
import json
import os
from pathlib import Path
import platform
import resource
import secrets
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest


def atomic_publish(directory: Path, final_name: str, payload: dict) -> Path:
    """Write/fsync a private staging file, then atomically link its final name."""
    if Path(final_name).name != final_name or final_name in ("", ".", ".."):
        raise ValueError("final_name must be one plain path component")
    if (os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd
            or os.link not in os.supports_dir_fd
            or os.stat not in os.supports_follow_symlinks
            or os.link not in os.supports_follow_symlinks
            or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")):
        raise RuntimeError("required no-follow directory-relative primitives unavailable")

    directory = directory.resolve(strict=True)
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    staging_name = f".atomic-publication-{secrets.token_hex(16)}.tmp"
    staging_created = False
    file_fd = None
    try:
        file_fd = os.open(
            staging_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory_fd,
        )
        staging_created = True
        with os.fdopen(file_fd, "w", encoding="utf-8", newline="\n") as stream:
            file_fd = None
            json.dump(payload, stream, ensure_ascii=True, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            staged = os.fstat(stream.fileno())
            os.link(
                staging_name, final_name,
                src_dir_fd=directory_fd, dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
            published = os.stat(final_name, dir_fd=directory_fd, follow_symlinks=False)
            if (not stat.S_ISREG(published.st_mode)
                    or (published.st_dev, published.st_ino) != (staged.st_dev, staged.st_ino)):
                raise RuntimeError("published entry does not match the fsynced staging inode")
        os.unlink(staging_name, dir_fd=directory_fd)
        staging_created = False
        os.fsync(directory_fd)
    except BaseException:
        if file_fd is not None:
            try:
                os.close(file_fd)
            except OSError:
                pass
        if staging_created:
            try:
                os.unlink(staging_name, dir_fd=directory_fd)
            except OSError:
                pass
        raise
    finally:
        os.close(directory_fd)
    return directory / final_name


class AtomicPublicationTests(unittest.TestCase):
    def test_platform_primitives_and_complete_publication(self):
        self.assertIn(os.link, os.supports_dir_fd)
        self.assertIn(os.link, os.supports_follow_symlinks)
        self.assertIn(os.stat, os.supports_dir_fd)
        self.assertIn(os.stat, os.supports_follow_symlinks)
        with tempfile.TemporaryDirectory(prefix="atomic-publish-") as temp:
            directory = Path(temp).resolve(strict=True)
            target = atomic_publish(directory, "result.json", {"status": "complete", "items": [1, 2, 3]})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")),
                             {"status": "complete", "items": [1, 2, 3]})
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(directory.iterdir()), [target])

    def test_concurrent_publishers_have_exactly_one_winner(self):
        with tempfile.TemporaryDirectory(prefix="atomic-race-") as temp:
            directory = Path(temp)
            barrier = threading.Barrier(2)

            def attempt(index: int) -> str:
                barrier.wait()
                try:
                    atomic_publish(directory, "winner.json", {"winner": index})
                    return "PUBLISHED"
                except FileExistsError:
                    return "EXISTS"

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(attempt, (1, 2)))
            self.assertEqual(sorted(outcomes), ["EXISTS", "PUBLISHED"])
            result = json.loads((directory / "winner.json").read_text(encoding="utf-8"))
            self.assertIn(result["winner"], (1, 2))
            self.assertEqual(list(directory.iterdir()), [directory / "winner.json"])

    def test_existing_symlink_is_not_followed_or_replaced(self):
        with tempfile.TemporaryDirectory(prefix="atomic-symlink-") as temp:
            directory = Path(temp)
            sentinel = directory / "sentinel.txt"
            sentinel.write_text("unchanged", encoding="utf-8")
            target = directory / "result.json"
            target.symlink_to(sentinel)
            with self.assertRaises(FileExistsError):
                atomic_publish(directory, "result.json", {"status": "must-not-publish"})
            self.assertTrue(target.is_symlink())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")

    def test_permission_denial_does_not_publish(self):
        if os.geteuid() == 0:
            self.skipTest("root bypasses directory mode permission checks")
        with tempfile.TemporaryDirectory(prefix="atomic-permission-") as temp:
            directory = Path(temp)
            target = directory / "denied.json"
            os.chmod(directory, 0o500)
            try:
                with self.assertRaises(PermissionError):
                    atomic_publish(directory, "denied.json", {"status": "not-written"})
                self.assertFalse(target.exists())
            finally:
                os.chmod(directory, 0o700)

    def test_process_kill_after_publish_keeps_final_file_complete(self):
        with tempfile.TemporaryDirectory(prefix="atomic-post-publish-kill-") as temp:
            directory = Path(temp).resolve(strict=True)
            marker = directory / ".directory-fsync-paused"
            target = directory / "published.json"
            child = subprocess.Popen(
                [sys.executable, __file__, "--crash-after-publish", str(directory), str(marker)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            try:
                deadline = time.monotonic() + 10
                while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(marker.exists(), "child did not reach the pre-directory-fsync boundary")
                child.kill()
                child.wait(timeout=5)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=5)
            self.assertTrue(target.is_file())
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")),
                             {"status": "complete", "payload": "fully-staged"})
            self.assertEqual({item.name for item in directory.iterdir()},
                             {".directory-fsync-paused", "published.json"})

    def test_process_kill_during_staging_never_publishes_final_name(self):
        with tempfile.TemporaryDirectory(prefix="atomic-kill-") as temp:
            directory = Path(temp)
            target = directory / "complete.json"
            child = subprocess.run(
                [sys.executable, __file__, "--crash-child", str(directory)],
                capture_output=True, text=True, timeout=20,
            )
            self.assertNotEqual(child.returncode, 0, child.stdout + child.stderr)
            self.assertFalse(target.exists(), "final name must not expose a partial write")
            staging = list(directory.glob(".atomic-publication-*.tmp"))
            self.assertEqual(len(staging), 1)
            self.assertEqual(staging[0].stat().st_mode & 0o777, 0o600)
            self.assertLessEqual(staging[0].stat().st_size, 4096)


def crash_after_publish_child(directory: Path, marker: Path) -> None:
    real_fsync = os.fsync
    calls = 0

    def pause_before_directory_fsync(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            marker.write_text("ready", encoding="utf-8")
            time.sleep(30)
        real_fsync(fd)

    os.fsync = pause_before_directory_fsync
    atomic_publish(directory, "published.json", {"status": "complete", "payload": "fully-staged"})


def crash_child(directory: Path) -> None:
    signal.signal(signal.SIGXFSZ, signal.SIG_DFL)
    resource.setrlimit(resource.RLIMIT_FSIZE, (4096, 4096))
    atomic_publish(directory, "complete.json", {"payload": "x" * 2_000_000})


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--crash-child":
        crash_child(Path(sys.argv[2]))
        return 0
    if len(sys.argv) == 4 and sys.argv[1] == "--crash-after-publish":
        crash_after_publish_child(Path(sys.argv[2]), Path(sys.argv[3]))
        return 0
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AtomicPublicationTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {
        "schema": "generic-atomic-file-publication-probe-v1",
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "os_link_dir_fd": os.link in os.supports_dir_fd,
        "os_link_no_follow": os.link in os.supports_follow_symlinks,
        "os_stat_dir_fd": os.stat in os.supports_dir_fd,
        "os_stat_no_follow": os.stat in os.supports_follow_symlinks,
    }
    Path("atomic-file-publication-receipt.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
