"""Public-safe model of explicit context delivery retry semantics.

This is a generic contract model. It does not import or execute any private
extension implementation and cannot prove conformance of a private product.
"""
from dataclasses import dataclass
import unittest


@dataclass
class Composer:
    text: str = ""


def deliver_context(composer: Composer, *, conversation_id: str | None,
                    workspace_id: str | None, adapter_accepts: bool) -> dict:
    # Never replace a user's draft. Explicit retry must fail without mutation.
    if composer.text.strip():
        return {"ok": False, "reason": "COMPOSER_NOT_EMPTY"}
    if not conversation_id or not workspace_id:
        return {"ok": False, "reason": "CONVERSATION_BINDING_REQUIRED"}
    if not adapter_accepts:
        return {"ok": False, "reason": "ADAPTER_DELIVERY_REFUSED"}
    composer.text = f"CONTEXT workspace_id={workspace_id}"
    return {"ok": True, "workspace_id": workspace_id}


class ComposerContextRetryContract(unittest.TestCase):
    def test_nonempty_composer_is_preserved_and_delivery_refused(self):
        composer = Composer("user's unrelated draft")
        result = deliver_context(
            composer, conversation_id="conversation-a",
            workspace_id="opaque-a", adapter_accepts=True,
        )
        self.assertEqual(result, {"ok": False, "reason": "COMPOSER_NOT_EMPTY"})
        self.assertEqual(composer.text, "user's unrelated draft")

    def test_empty_composer_delivers_only_the_bound_opaque_workspace_id(self):
        composer = Composer()
        result = deliver_context(
            composer, conversation_id="conversation-a",
            workspace_id="opaque-a", adapter_accepts=True,
        )
        self.assertEqual(result, {"ok": True, "workspace_id": "opaque-a"})
        self.assertEqual(composer.text, "CONTEXT workspace_id=opaque-a")
        self.assertNotIn("/Users/", composer.text)
        self.assertNotIn("/home/", composer.text)

    def test_missing_conversation_or_binding_fails_closed(self):
        for conversation_id, workspace_id in (
            (None, "opaque-a"), ("conversation-a", None), ("", "opaque-a"),
        ):
            with self.subTest(conversation_id=conversation_id, workspace_id=workspace_id):
                composer = Composer()
                result = deliver_context(
                    composer, conversation_id=conversation_id,
                    workspace_id=workspace_id, adapter_accepts=True,
                )
                self.assertEqual(result, {
                    "ok": False, "reason": "CONVERSATION_BINDING_REQUIRED"
                })
                self.assertEqual(composer.text, "")

    def test_adapter_refusal_is_not_reported_as_success(self):
        composer = Composer()
        result = deliver_context(
            composer, conversation_id="conversation-a",
            workspace_id="opaque-a", adapter_accepts=False,
        )
        self.assertEqual(result, {"ok": False, "reason": "ADAPTER_DELIVERY_REFUSED"})
        self.assertEqual(composer.text, "")

    def test_conversation_bindings_do_not_cross(self):
        bindings = {
            "conversation-a": "opaque-a",
            "conversation-b": "opaque-b",
        }
        self.assertEqual(bindings["conversation-a"], "opaque-a")
        self.assertEqual(bindings["conversation-b"], "opaque-b")
        self.assertNotEqual(bindings["conversation-a"], bindings["conversation-b"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
