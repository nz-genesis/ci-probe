import hashlib
import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).parent


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


capture = load_module("p347_n100_capture", "capture.py")
manifest = load_module("p347_n100_manifest", "manifest.py")


class CaptureContractTests(unittest.TestCase):
    def test_sha256_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "payload.bin"
            path.write_bytes(b"abc")
            self.assertEqual(capture.sha256(path), hashlib.sha256(b"abc").hexdigest())

    def test_filter_uses_actor_and_mac_observed_target_ips(self):
        value = capture.build_capture_filter(
            "192.0.2.10",
            ["198.51.100.20", "2001:db8::20", "198.51.100.20"],
            443,
        )
        self.assertEqual(
            value,
            "host 192.0.2.10 and (host 198.51.100.20 or host 2001:db8::20) and port 443",
        )

    def test_filter_rejects_non_literal_actor_ip(self):
        with self.assertRaisesRegex(ValueError, "actor IP"):
            capture.build_capture_filter("actor-host", ["198.51.100.20"], 443)

    def test_filter_rejects_non_literal_target_ip(self):
        with self.assertRaisesRegex(ValueError, "target IP"):
            capture.build_capture_filter("192.0.2.10", ["authority.example"], 443)

    def test_filter_rejects_invalid_port(self):
        with self.assertRaisesRegex(ValueError, "target port"):
            capture.build_capture_filter("192.0.2.10", ["198.51.100.20"], 70000)

    def test_capture_directory_accepts_empty_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "fresh-run"
            resolved = capture.require_empty_directory(output)
            self.assertTrue(resolved.is_dir())
            self.assertEqual(list(resolved.iterdir()), [])

    def test_capture_directory_rejects_stale_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "reused-run"
            output.mkdir()
            (output / "witness.pcap").write_bytes(b"stale")
            with self.assertRaisesRegex(RuntimeError, "must be empty"):
                capture.require_empty_directory(output)

    def test_manifest_rejects_incomplete_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "capture evidence incomplete"):
                manifest.validate_capture(pathlib.Path(directory))

    def test_manifest_rejects_stale_temporary_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "manifest.json.tmp").write_text("stale", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "stale manifest.json.tmp"):
                manifest.build_manifest(root)


if __name__ == "__main__":
    unittest.main()
