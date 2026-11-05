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
from unittest import mock


def open_directory_no_follow(directory: Path) -> tuple[int, tuple[tuple[int, int], ...]]:
    """Open every absolute path component and retain its device/inode chain."""
    if not directory.is_absolute():
        raise ValueError("directory must be absolute")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    current_fd = os.open(os.sep, flags)
    identities = []
    try:
        root_stat = os.fstat(current_fd)
        identities.append((root_stat.st_dev, root_stat.st_ino))
        for component in directory.parts[1:]:
            if component in ("", ".", ".."):
                raise ValueError("non-canonical path component")
            next_fd = os.open(component, flags, dir_fd=current_fd)
            try:
                next_stat = os.fstat(next_fd)
                identities.append((next_stat.st_dev, next_stat.st_ino))
            except BaseException:
                try:
                    os.close(next_fd)
                except OSError:
                    pass
                raise
            try:
                os.close(current_fd)
            except BaseException:
                try:
                    os.close(next_fd)
                except OSError:
                    pass
                raise
            current_fd = next_fd
        return current_fd, tuple(identities)
    except BaseException:
        try:
            os.close(current_fd)
        except OSError:
            pass
        raise


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
    directory_fd, expected_chain = open_directory_no_follow(directory)
    try:
        confirm_fd, confirmed_chain = open_directory_no_follow(directory)
    except OSError as exc:
        os.close(directory_fd)
        raise RuntimeError("parent path chain changed during preflight") from exc
    os.close(confirm_fd)
    if confirmed_chain != expected_chain:
        os.close(directory_fd)
        raise RuntimeError("parent path chain changed during preflight")
    staging_name = None
    staging_created = False
    file_fd = None
    published_identity = None
    try:
        staging_name = f".atomic-publication-{secrets.token_hex(16)}.tmp"
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
            published_identity = (published.st_dev, published.st_ino)
        os.unlink(staging_name, dir_fd=directory_fd)
        staging_created = False
        os.fsync(directory_fd)
        try:
            check_fd, published_chain = open_directory_no_follow(directory)
        except OSError:
            published_chain = None
            check_fd = None
        if check_fd is not None:
            os.close(check_fd)
        if published_chain != expected_chain:
            try:
                current_final = os.stat(
                    final_name, dir_fd=directory_fd, follow_symlinks=False
                )
                if (not stat.S_ISREG(current_final.st_mode)
                        or published_identity is None
                        or (current_final.st_dev, current_final.st_ino) != published_identity):
                    raise RuntimeError(
                        "final-name changed before cleanup; refusing to remove unrelated entry"
                    )
                os.unlink(final_name, dir_fd=directory_fd)
                os.fsync(directory_fd)
            except (OSError, RuntimeError) as cleanup_error:
                raise RuntimeError("parent path chain changed and final-name cleanup failed") from cleanup_error
            raise RuntimeError("parent path chain changed during publication")
    except BaseException:
        if file_fd is not None:
            try:
                os.close(file_fd)
            except OSError:
                pass
        if staging_created and staging_name is not None:
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

    def test_real_ancestor_directory_replacement_is_detected_before_write(self):
        with tempfile.TemporaryDirectory(prefix="atomic-parent-inode-race-") as temp:
            root = Path(temp)
            ancestor = root / "ancestor"
            parent = ancestor / "reports"
            parent.mkdir(parents=True)
            moved = root / "ancestor-original"
            real_open = os.open
            replaced = {"value": False}

            def replace_ancestor_before_open(path, flags, *args, dir_fd=None, **kwargs):
                if path == "reports" and dir_fd is not None and not replaced["value"]:
                    os.rename(ancestor, moved)
                    (ancestor / "reports").mkdir(parents=True)
                    replaced["value"] = True
                return real_open(path, flags, *args, dir_fd=dir_fd, **kwargs)

            supported_dir_fd = os.supports_dir_fd
            with mock.patch.object(os, "open", side_effect=replace_ancestor_before_open) as wrapped_open:
                with mock.patch.object(os, "supports_dir_fd", supported_dir_fd | {wrapped_open}):
                    with self.assertRaisesRegex(RuntimeError, "parent path chain changed during preflight"):
                        atomic_publish(parent, "race.json", {"status": "must-not-publish"})
            self.assertTrue(replaced["value"])
            self.assertEqual(list((moved / "reports").iterdir()), [])
            self.assertEqual(list((ancestor / "reports").iterdir()), [])

    def test_ancestor_symlink_replacement_does_not_redirect_publication(self):
        with tempfile.TemporaryDirectory(prefix="atomic-parent-race-") as temp:
            root = Path(temp)
            ancestor = root / "ancestor"
            parent = ancestor / "reports"
            parent.mkdir(parents=True)
            moved = root / "ancestor-moved"
            redirect = root / "redirect"
            redirected_parent = redirect / "reports"
            redirected_parent.mkdir(parents=True)
            real_open = os.open
            swapped = {"value": False}

            def replace_ancestor_before_child_open(path, flags, *args, dir_fd=None, **kwargs):
                if path == "reports" and dir_fd is not None and not swapped["value"]:
                    os.rename(ancestor, moved)
                    os.symlink(redirect, ancestor, target_is_directory=True)
                    swapped["value"] = True
                return real_open(path, flags, *args, dir_fd=dir_fd, **kwargs)

            supported_dir_fd = os.supports_dir_fd
            with mock.patch.object(os, "open", side_effect=replace_ancestor_before_child_open) as wrapped_open:
                with mock.patch.object(os, "supports_dir_fd", supported_dir_fd | {wrapped_open}):
                    with self.assertRaisesRegex(RuntimeError, "parent path chain changed during preflight"):
                        atomic_publish(parent, "race.json", {"status": "must-not-publish"})
            self.assertTrue(swapped["value"])
            self.assertFalse((moved / "reports" / "race.json").exists())
            self.assertFalse((redirected_parent / "race.json").exists())
            self.assertEqual(list((moved / "reports").iterdir()), [])
            self.assertEqual(list(redirected_parent.iterdir()), [])

    def test_child_directory_fd_is_closed_when_fstat_fails(self):
        with tempfile.TemporaryDirectory(prefix="atomic-fstat-close-") as temp:
            directory = Path(temp).resolve(strict=True)
            (directory / "child").mkdir()
            real_open = os.open
            real_fstat = os.fstat
            opened = []

            def capture_open(*args, **kwargs):
                fd = real_open(*args, **kwargs)
                opened.append(fd)
                return fd

            def fail_child_fstat(fd):
                if len(opened) == 2 and fd == opened[-1]:
                    raise OSError("injected child fstat failure")
                return real_fstat(fd)

            with mock.patch.object(os, "open", side_effect=capture_open):
                with mock.patch.object(os, "fstat", side_effect=fail_child_fstat):
                    with self.assertRaisesRegex(OSError, "injected child fstat failure"):
                        open_directory_no_follow(directory / "child")

            self.assertEqual(len(opened), 2)
            with self.assertRaises(OSError):
                real_fstat(opened[1])

    def test_parent_directory_fd_is_closed_when_staging_token_fails(self):
        with tempfile.TemporaryDirectory(prefix="atomic-token-close-") as temp:
            directory = Path(temp).resolve(strict=True)
            real_open = os.open
            real_fstat = os.fstat
            opened_directory_fds = []

            def capture_directory_open(*args, **kwargs):
                fd = real_open(*args, **kwargs)
                if stat.S_ISDIR(real_fstat(fd).st_mode):
                    opened_directory_fds.append(fd)
                return fd

            supported_dir_fd = os.supports_dir_fd
            with mock.patch.object(os, "open", side_effect=capture_directory_open) as wrapped_open:
                with mock.patch.object(os, "supports_dir_fd", supported_dir_fd | {wrapped_open}):
                    with mock.patch.object(
                        secrets, "token_hex", side_effect=OSError("injected token source failure")
                    ):
                        with self.assertRaisesRegex(OSError, "injected token source failure"):
                            atomic_publish(directory, "report.json", {"status": "not-written"})

            self.assertTrue(opened_directory_fds)
            for fd in opened_directory_fds:
                with self.assertRaises(OSError):
                    real_fstat(fd)

    def test_chain_mismatch_cleanup_does_not_unlink_replaced_final_entry(self):
        with tempfile.TemporaryDirectory(prefix="atomic-chain-cleanup-race-") as temp:
            root = Path(temp).resolve(strict=True)
            ancestor = root / "ancestor"
            parent = ancestor / "reports"
            parent.mkdir(parents=True)
            moved = root / "ancestor-original"
            real_fsync = os.fsync
            replaced = {"value": False}
            output = parent / "race.json"

            def replace_parent_and_final_before_directory_fsync(fd):
                current = os.fstat(fd)
                if stat.S_ISDIR(current.st_mode) and not replaced["value"]:
                    os.rename(ancestor, moved)
                    ancestor.mkdir(mode=0o777)
                    os.rename(moved / "reports", ancestor / "reports")
                    output.unlink()
                    output.write_text("foreign-entry", encoding="utf-8")
                    replaced["value"] = True
                return real_fsync(fd)

            with mock.patch.object(
                os, "fsync", side_effect=replace_parent_and_final_before_directory_fsync
            ):
                with self.assertRaisesRegex(
                    RuntimeError, "parent path chain changed and final-name cleanup failed"
                ) as caught:
                    atomic_publish(parent, "race.json", {"status": "must-not-publish"})

            self.assertTrue(replaced["value"])
            self.assertIn("refusing to remove unrelated entry", str(caught.exception.__cause__))
            self.assertEqual(output.read_text(encoding="utf-8"), "foreign-entry")
            self.assertEqual(list((ancestor / "reports").iterdir()), [output])
            self.assertEqual(list(moved.iterdir()), [])

    def test_ancestor_replacement_with_same_parent_inode_is_detected(self):
        with tempfile.TemporaryDirectory(prefix="atomic-chain-race-") as temp:
            root = Path(temp)
            ancestor = root / "ancestor"
            parent = ancestor / "reports"
            parent.mkdir(parents=True)
            moved = root / "ancestor-original"
            real_fsync = os.fsync
            replaced = {"value": False}

            def replace_ancestor_before_directory_fsync(fd):
                current = os.fstat(fd)
                if stat.S_ISDIR(current.st_mode) and not replaced["value"]:
                    os.rename(ancestor, moved)
                    ancestor.mkdir(mode=0o777)
                    os.rename(moved / "reports", ancestor / "reports")
                    replaced["value"] = True
                return real_fsync(fd)

            with mock.patch.object(os, "fsync", side_effect=replace_ancestor_before_directory_fsync):
                with self.assertRaisesRegex(
                    RuntimeError, "parent path chain changed during publication"
                ):
                    atomic_publish(parent, "race.json", {"status": "must-not-publish"})

            self.assertTrue(replaced["value"])
            self.assertFalse((ancestor / "reports" / "race.json").exists())
            self.assertEqual(list((ancestor / "reports").iterdir()), [])
            self.assertEqual(list(moved.iterdir()), [])

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
