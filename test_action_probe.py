import unittest

from action_probe import (
    ActionContract,
    AdmissionError,
    DuplicateExecutionError,
    Status,
    admit,
    execute_once,
    observe,
    safe_retry,
    verify,
)


class ActionSemanticsTests(unittest.TestCase):
    def contract(self, *, authority="test-authority"):
        return ActionContract(
            target="fixture-target",
            operation="set-value",
            inputs={"value": 42},
            required_capability="fixture-write",
            authority=authority,
            expected_outcome={"value": 42},
            verification={"source": "fixture"},
        )

    def admitted(self):
        return admit(
            self.contract(),
            capabilities={"fixture-write"},
            authorities={"test-authority"},
        )

    def test_admission_requires_capability_and_authority(self):
        with self.assertRaises(AdmissionError):
            admit(self.contract(), capabilities=set(), authorities={"test-authority"})
        with self.assertRaises(AdmissionError):
            admit(self.contract(), capabilities={"fixture-write"}, authorities=set())

    def test_success_requires_observed_and_verified_outcome(self):
        record = execute_once(self.admitted(), effect={"value": 42})
        self.assertEqual(record.status, Status.COMPLETED)
        self.assertNotEqual(record.status, Status.VERIFIED)
        verify(observe(record, {"value": 42}), {"value": 42})
        self.assertEqual(record.status, Status.VERIFIED)

    def test_executor_success_is_not_world_effect_verification(self):
        record = execute_once(self.admitted(), effect={"value": 42})
        verify(observe(record, {"value": 41}), {"value": 42})
        self.assertEqual(record.status, Status.VERIFICATION_FAILED)

    def test_lost_acknowledgement_is_unknown_and_not_safe_to_retry(self):
        record = execute_once(self.admitted(), effect={"value": 42}, acknowledgement_lost=True)
        self.assertEqual(record.status, Status.UNKNOWN)
        self.assertFalse(safe_retry(record))
        with self.assertRaises(DuplicateExecutionError):
            execute_once(record, effect={"value": 42})

    def test_admission_scope_is_not_executor_scope(self):
        record = self.admitted()
        record.trace.append("executor-requested-extra-scope")
        # The generic probe has no API for silently expanding the contract.
        self.assertEqual(record.status, Status.ADMITTED)
        self.assertEqual(record.action_id, "fixture-target:set-value")

    def test_realization_is_replaceable_at_contract_boundary(self):
        first = execute_once(self.admitted(), effect={"value": 42})
        second = execute_once(self.admitted(), effect={"value": 42})
        self.assertEqual(first.outcome, second.outcome)
        self.assertEqual(first.status, second.status)


if __name__ == "__main__":
    unittest.main()
