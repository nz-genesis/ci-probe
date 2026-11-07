import unittest

from action_probe.scenario_matrix import SCENARIOS, EffectCertainty, State, new_operation_retry_candidate


class ScenarioMatrixTests(unittest.TestCase):
    def scenario(self, name):
        return next(item for item in SCENARIOS if item.name == name)

    def test_revocation_blocks_retry_without_fresh_admission(self):
        item = self.scenario("revoked_before_execution")
        self.assertEqual(item.expected, (State.REJECTED,))
        self.assertFalse(item.new_operation_retry_candidate)

    def test_failed_status_alone_does_not_authorize_new_operation_retry(self):
        self.assertFalse(new_operation_retry_candidate(State.FAILED, EffectCertainty.POSSIBLE))
        self.assertFalse(new_operation_retry_candidate(State.FAILED, EffectCertainty.PARTIAL))
        self.assertTrue(new_operation_retry_candidate(State.FAILED, EffectCertainty.NO_EFFECT_CONFIRMED))

    def test_unknown_never_gets_blind_retry(self):
        self.assertFalse(new_operation_retry_candidate(State.UNKNOWN, EffectCertainty.POSSIBLE))
        self.assertFalse(new_operation_retry_candidate(State.UNKNOWN, EffectCertainty.NO_EFFECT_CONFIRMED))

    def test_reconciliation_no_effect_is_only_a_new_operation_candidate(self):
        item = self.scenario("reconciled_not_applied")
        self.assertEqual(item.expected, (State.RECONCILED,))
        self.assertTrue(item.new_operation_retry_candidate)

    def test_partial_effect_requires_reconciliation(self):
        item = self.scenario("partial_effect")
        self.assertIn(State.PARTIAL, item.expected)
        self.assertIn(State.UNKNOWN, item.expected)
        self.assertFalse(item.new_operation_retry_candidate)

    def test_success_requires_verification(self):
        item = self.scenario("successful_execution")
        self.assertEqual(item.expected[-1], State.VERIFIED)
        self.assertFalse(item.new_operation_retry_candidate)

    def test_unresolved_reconciliation_is_not_retryable(self):
        item = self.scenario("reconciliation_unresolved")
        self.assertEqual(item.expected, (State.UNRESOLVED,))
        self.assertFalse(item.new_operation_retry_candidate)


if __name__ == "__main__":
    unittest.main()
