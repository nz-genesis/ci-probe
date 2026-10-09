import unittest
from unittest.mock import Mock

import authority_readiness as readiness


def response(status, body, local="192.0.2.10", remote="198.51.100.20", transport="HTTP_RESPONSE_OBSERVED"):
    return {
        "http_status": status,
        "response_body": body,
        "local_ip": local,
        "remote_ip": remote,
        "remote_port": 443,
        "transport_state": transport,
        "request_started_utc": "2026-10-09T09:00:00+00:00",
        "request_finished_utc": "2026-10-09T09:00:01+00:00",
    }


class AuthorityReadinessTests(unittest.TestCase):
    def test_known_1042_propagation_retries_then_accepts_exact_source(self):
        transient = response(404, {"error_code": 1042})
        ready = response(200, {
            "authority": "P347_EXTERNAL_AUTHORITY",
            "source_version": "sha",
        })
        request = Mock(side_effect=[transient, ready])
        sleep = Mock()
        attempts, ok, error = readiness.one_probe(
            "https://authority.workers.dev", "sha", request, sleep,
            max_attempts=5, interval_seconds=2,
        )
        self.assertTrue(ok)
        self.assertIsNone(error)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(2)
        self.assertEqual(attempts[-1]["result"]["remote_ip"], "198.51.100.20")

    def test_cloudflare_403_challenge_fails_closed_without_retry_or_raw_html(self):
        challenge = response(403, {
            "raw": '<html><title>Just a moment...</title><script>__cf_chl_tk=secret</script></html>'
        })
        request = Mock(return_value=challenge)
        sleep = Mock()
        attempts, ok, error = readiness.one_probe(
            "https://authority.workers.dev", "sha", request, sleep,
            max_attempts=30, interval_seconds=2,
        )
        self.assertFalse(ok)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(request.call_count, 1)
        sleep.assert_not_called()
        body = attempts[0]["result"]["response_body"]
        self.assertTrue(body["cloudflare_challenge_detected"])
        self.assertTrue(body["raw_body_redacted"])
        self.assertNotIn("secret", str(body))
        self.assertNotIn("__cf_chl_tk", str(body))

    def test_source_version_mismatch_fails_closed_without_retry(self):
        mismatch = response(200, {
            "authority": "P347_EXTERNAL_AUTHORITY",
            "source_version": "different-sha",
        })
        request = Mock(return_value=mismatch)
        attempts, ok, error = readiness.one_probe(
            "https://authority.workers.dev", "expected-sha", request, Mock(),
            max_attempts=30,
        )
        self.assertFalse(ok)
        self.assertEqual(error, "authority source_version mismatch")
        self.assertEqual(request.call_count, 1)

    def test_retry_budget_is_bounded_for_known_transient_responses(self):
        transient = response(500, {"error_code": 1104})
        request = Mock(return_value=transient)
        sleep = Mock()
        attempts, ok, error = readiness.one_probe(
            "https://authority.workers.dev", "sha", request, sleep,
            max_attempts=4, interval_seconds=2,
        )
        self.assertFalse(ok)
        self.assertEqual(len(attempts), 4)
        self.assertEqual(request.call_count, 4)
        self.assertEqual(sleep.call_count, 3)


if __name__ == "__main__":
    unittest.main()
