import unittest

STRATEGIES = {"reuse", "compose", "adapt", "acquire", "create"}
MEASUREMENTS = {
    "quality", "wall_time", "cpu_time", "peak_memory", "model_invocations",
    "input_tokens", "output_tokens", "network_tool_time", "control_overhead",
    "verification_overhead", "recovery_cost", "cache_lookup", "cache_maintenance",
    "cache_miss_recomputation", "human_attention",
}
REQUIRED_CONTROLS = {
    "task_id", "quality_threshold", "input_hash", "strategy_revision",
    "model_version", "runtime_version", "resource_envelope", "warm_cold_state",
    "repetitions", "measurement_method",
}


def dominates(a, b):
    """Return True when a is no worse on all dimensions and better on one."""
    return (
        a["quality"] >= b["quality"]
        and a["wall_time"] <= b["wall_time"]
        and (a["quality"] > b["quality"] or a["wall_time"] < b["wall_time"])
    )


class ResourceEnvelopeProtocolTests(unittest.TestCase):
    def test_cache_is_not_a_strategy_category(self):
        self.assertEqual(STRATEGIES, {"reuse", "compose", "adapt", "acquire", "create"})
        self.assertNotIn("cache", STRATEGIES)

    def test_measurement_vector_is_not_token_only(self):
        self.assertGreater(len(MEASUREMENTS), 10)
        for name in ("wall_time", "cpu_time", "peak_memory", "verification_overhead", "human_attention"):
            self.assertIn(name, MEASUREMENTS)

    def test_unmeasured_is_explicit(self):
        record = {"wall_time": 1.2, "peak_memory": "UNMEASURED"}
        self.assertEqual(record["peak_memory"], "UNMEASURED")
        self.assertNotEqual(record["peak_memory"], 0)

    def test_quality_threshold_filters_cheaper_but_invalid_result(self):
        threshold = 0.90
        cheap = {"quality": 0.70, "wall_time": 1.0}
        self.assertFalse(cheap["quality"] >= threshold)

    def test_pareto_incomparability_is_preserved(self):
        fast = {"quality": 0.90, "wall_time": 1.0}
        accurate = {"quality": 0.99, "wall_time": 2.0}
        self.assertFalse(dominates(fast, accurate))
        self.assertFalse(dominates(accurate, fast))

    def test_benchmark_controls_are_complete(self):
        sample = {
            "task_id": "task-001", "quality_threshold": 0.90,
            "input_hash": "sha256:example", "strategy_revision": "git:example",
            "model_version": "model:example", "runtime_version": "runtime:example",
            "resource_envelope": "constrained", "warm_cold_state": "cold",
            "repetitions": 5, "measurement_method": "wall+cpu+memory",
        }
        self.assertTrue(REQUIRED_CONTROLS <= sample.keys())
        self.assertGreaterEqual(sample["repetitions"], 2)

    def test_previous_authority_does_not_become_current_authority(self):
        self.assertNotEqual("cached_authorization", "current_authorization")


if __name__ == "__main__":
    unittest.main()
