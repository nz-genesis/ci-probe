import unittest

from action_probe import (
    ActionContract, AdmissionError, AuthorizationRevokedError,
    CapabilityRevokedError, ExecutionRecord, ScopeViolationError,
    Status, admit, execute_once, observe, reconcile, safe_retry, verify,
)


class ActionSemanticsTests(unittest.TestCase):
    def contract(self, *, authority="test-authority", target="fixture-target", operation="set-value"):
        return ActionContract(
            target=target, operation=operation, inputs={"value": 42},
            required_capability="fixture-write", authority=authority,
            expected_outcome={"value": 42}, verification={"source": "fixture"},
            idempotency_key="fixture-action-42",
        )

    def admitted(self, *, authority="test-authority", target="fixture-target", operation="set-value"):
        return admit(self.contract(authority=authority, target=target, operation=operation),
                     capabilities={"fixture-write"}, authorities={authority})

    def execute(self, record, *, target=None, operation=None, capabilities=None, authorities=None,
                acknowledgement_lost=False):
        return execute_once(
            record, effect={"value": 42},
            target=record.target if target is None else target,
            operation=record.operation if operation is None else operation,
            active_capabilities={"fixture-write"} if capabilities is None else capabilities,
            active_authorities={record.authority} if authorities is None else authorities,
            acknowledgement_lost=acknowledgement_lost,
        )

    def test_admission_requires_capability_and_authority(self):
        with self.assertRaises(AdmissionError):
            admit(self.contract(), capabilities=set(), authorities={"test-authority"})
        with self.assertRaises(AdmissionError):
            admit(self.contract(), capabilities={"fixture-write"}, authorities=set())

    def test_success_requires_observed_and_verified_outcome(self):
        record = self.execute(self.admitted())
        self.assertEqual(record.status, Status.COMPLETED)
        self.assertNotEqual(record.status, Status.VERIFIED)
        verify(observe(record, {"value": 42}), {"value": 42})
        self.assertEqual(record.status, Status.VERIFIED)

    def test_executor_success_is_not_world_effect_verification(self):
        record = self.execute(self.admitted())
        verify(observe(record, {"value": 41}), {"value": 42})
        self.assertEqual(record.status, Status.VERIFICATION_FAILED)

    def test_lost_acknowledgement_is_unknown_and_not_safe_to_retry(self):
        record = self.execute(self.admitted(), acknowledgement_lost=True)
        self.assertEqual(record.status, Status.UNKNOWN)
        self.assertFalse(safe_retry(record))
        with self.assertRaises(AdmissionError):
            self.execute(record)

    def test_unknown_requires_reconciliation_before_verification(self):
        record = self.execute(self.admitted(), acknowledgement_lost=True)
        with self.assertRaises(AdmissionError):
            verify(record, {"value": 42})
        reconcile(record, {"value": 42})
        verify(record, {"value": 42})
        self.assertEqual(record.status, Status.VERIFIED)
        self.assertFalse(safe_retry(record))

    def test_forged_unknown_without_attempt_cannot_execute_or_reconcile(self):
        record = ExecutionRecord("forged", status=Status.UNKNOWN, attempts=0)
        with self.assertRaises(AdmissionError):
            self.execute(record)
        with self.assertRaises(AdmissionError):
            reconcile(record, {"value": 42})

    def test_forged_completed_without_attempt_cannot_verify(self):
        record = ExecutionRecord("forged", status=Status.COMPLETED, attempts=0,
                                 observed={"value": 42}, observation_recorded=True)
        with self.assertRaises(AdmissionError):
            verify(record, {"value": 42})

    def test_executor_cannot_expand_target_or_operation_scope(self):
        record = self.admitted()
        with self.assertRaises(ScopeViolationError):
            self.execute(record, target="other-target")
        with self.assertRaises(ScopeViolationError):
            self.execute(record, operation="delete-value")
        self.assertEqual(record.attempts, 0)

    def test_delimiter_in_identifiers_does_not_change_binding(self):
        record = self.admitted(target="fixture:target", operation="set:value")
        result = self.execute(record)
        self.assertEqual(result.target, "fixture:target")
        self.assertEqual(result.operation, "set:value")
        self.assertEqual(result.status, Status.COMPLETED)

    def test_revoked_authority_blocks_execution_even_if_another_exists(self):
        record = self.admitted()
        with self.assertRaises(AuthorizationRevokedError):
            self.execute(record, authorities={"other-authority"})
        self.assertEqual(record.attempts, 0)

    def test_revoked_capability_blocks_execution_even_if_another_exists(self):
        record = self.admitted()
        with self.assertRaises(CapabilityRevokedError):
            self.execute(record, capabilities={"other-capability"})
        self.assertEqual(record.attempts, 0)

    def test_concurrent_admissions_do_not_claim_exactly_once(self):
        first, second = self.admitted(), self.admitted()
        self.execute(first)
        self.execute(second)
        self.assertEqual(first.action_id, second.action_id)
        self.assertEqual((first.attempts, second.attempts), (1, 1))

    def test_realization_is_replaceable_at_contract_boundary(self):
        first, second = self.execute(self.admitted()), self.execute(self.admitted())
        self.assertEqual(first.outcome, second.outcome)
        self.assertEqual(first.status, second.status)


if __name__ == "__main__":
    unittest.main()
