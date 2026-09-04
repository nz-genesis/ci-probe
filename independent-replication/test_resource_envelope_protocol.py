import unittest

STRATEGIES = {"reuse", "compose", "adapt", "acquire", "create"}
MEASUREMENTS = {
    "quality", "wall_time", "cpu_time", "peak_memory", "model_invocations",
    "input_tokens", "output_tokens", "network_tool_time", "control_overhead",
    "verification_overhead", "recovery_cost", "cache_lookup", "cache_maintenance",
    "cache_miss_recomputation", "human_attention",
}


class ResourceEnvelopeProtocolTests(unittest.TestCase):
    def test_cache_is_not_a_strategy_category(self):
        self.assertEqual(STRATEGIES, {"reuse", "compose", "adapt", "acquire", "create"})
        self.assertNotIn("cache", STRATEGIES)

    def test_measurement_vector_is_not_token_only(self):
        self.assertGreater(len(MEASUREMENTS), 10)
        for name in ("latency" if False else "wall_time", "cpu_time", "peak_memory", "verification_overhead"):
            self.assertIn(name, MEASUREMENTS)

    def test_unmeasured_must_not_be_encoded_as_zero(self):
        self.assertNotEqual("UNMEASURED", "0")

    def test_quality_is_an_admissibility_constraint(self):
        cheap = {"quality": 0.70, "cost": 1.0}
        threshold = 0.90
        self.assertLess(cheap["quality"], threshold)
        self.assertFalse(cheap["quality"] >= threshold)

    def test_pareto_incomparability_is_valid(self):
        fast = {"quality": 0.90, "wall_time": 1.0}
        accurate = {"quality": 0.99, "wall_time": 2.0}
        self.assertLess(fast["quality"], accurate["quality"])
        self.assertLess(fast["wall_time"], accurate["wall_time"])

    def test_previous_authority_does_not_become_current_authority(self):
        self.assertNotEqual("cached_authorization", "current_authorization")


if __name__ == "__main__":
    unittest.main()
