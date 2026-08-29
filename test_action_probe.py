import unittest

from action_probe import (
    ActionContract,
    AdmissionError,
    AuthorizationRevokedError,
    DuplicateExecutionError,
    ScopeViolationError,
    Status,
    admit,
    execute_once,
    observe,
    reconcile,
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
            idempotency_key="fixture-action-42",
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

    def test_admission_requires_explicit_capability_and_authority_fields(self):
        contract = ActionContract(target="fixture-target", operation="set-value")
        with self.assertRaises(AdmissionError):
            admit(contract, capabilities=set(), authorities=set())

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

    def test_unknown_state_requires_reconciliation_before_classification(self):
        record = execute_once(self.admitted(), effect={"value": 42}, acknowledgement_lost=True)
        reconcile(record, {"value": 42})
        verify(record, {"value": 42})
        self.assertEqual(record.status, Status.VERIFIED)
        self.assertFalse(safe_retry(record))

    def test_executor_cannot_expand_target_or_operation_scope(self):
        record = self.admitted()
        with self.assertRaises(ScopeViolationError):
            execute_once(record, effect={"value": 42}, target="other-target")
        with self.assertRaises(ScopeViolationError):
            execute_once(record, effect={"value": 42}, operation="delete-value")
        self.assertEqual(record.attempts, 0)
        self.assertEqual(record.status, Status.ADMITTED)

    def test_revoked_authority_blocks_execution(self):
        record = self.admitted()
        with self.assertRaises(AuthorizationRevokedError):
            execute_once(record, effect={"value": 42}, active_authorities=set())
        self.assertEqual(record.attempts, 0)
        self.assertEqual(record.status, Status.ADMITTED)

    def test_concurrent_admissions_are_distinct_and_not_exactly_once(self):
        first = self.admitted()
        second = self.admitted()
        execute_once(first, effect={"value": 42})
        execute_once(second, effect={"value": 42})
        self.assertEqual(first.action_id, second.action_id)
        self.assertEqual(first.attempts, 1)
        self.assertEqual(second.attempts, 1)
        # The generic probe deliberately does not claim distributed locking
        # or exactly-once semantics; this is a negative boundary result.

    def test_realization_is_replaceable_at_contract_boundary(self):
        first = execute_once(self.admitted(), effect={"value": 42})
        second = execute_once(self.admitted(), effect={"value": 42})
        self.assertEqual(first.outcome, second.outcome)
        self.assertEqual(first.status, second.status)


if __name__ == "__main__":
    unittest.main()
