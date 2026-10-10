"""Public-safe generic contract probe for workspace lifecycle semantics.

This is a standalone contract model. It does NOT import or execute web2api-lab
private code and cannot prove that private implementation conforms to it.
"""
import json
import tempfile
import unittest
from pathlib import Path


class WorkspaceLifecycleContractTests(unittest.TestCase):
    def test_registry_reset_removes_metadata_not_filesystem_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "chosen-workspace"
            folder.mkdir()
            sentinel = folder / "sentinel.txt"
            sentinel.write_text("preserve-me", encoding="utf-8")

            registry = {
                "workspaces": [{"workspace_id": "ws-a", "root": str(folder)}],
                "creation_roots": [{"path": str(folder)}],
            }
            # Contract operation: clear registry metadata only.
            removed = {
                "workspaces": len(registry["workspaces"]),
                "creation_roots": len(registry["creation_roots"]),
            }
            registry["workspaces"] = []
            registry["creation_roots"] = []

            self.assertEqual(removed, {"workspaces": 1, "creation_roots": 1})
            self.assertEqual(registry, {"workspaces": [], "creation_roots": []})
            self.assertTrue(folder.is_dir())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve-me")

    def test_conversation_bindings_are_isolated(self):
        bindings = {
            "conversation-A": "workspace-A",
            "conversation-B": "workspace-B",
        }
        self.assertEqual(bindings["conversation-A"], "workspace-A")
        self.assertEqual(bindings["conversation-B"], "workspace-B")
        self.assertNotEqual(bindings["conversation-A"], bindings["conversation-B"])

    def test_reset_response_contract_has_bounded_nonnegative_counts(self):
        response = {"workspaces": 2, "creation_roots": 1}
        self.assertEqual(set(response), {"workspaces", "creation_roots"})
        for key in ("workspaces", "creation_roots"):
            self.assertIs(type(response[key]), int)
            self.assertGreaterEqual(response[key], 0)
            self.assertLessEqual(response[key], 1_000_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
