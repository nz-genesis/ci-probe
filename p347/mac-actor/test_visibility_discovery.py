import json
import unittest
from pathlib import Path
from unittest.mock import Mock
import visibility_discovery as discovery

def response(status,body,local="192.0.2.10",remote="198.51.100.20",transport="HTTP_RESPONSE_OBSERVED"):
    return {"http_status":status,"response_body":body,"local_ip":local,"remote_ip":remote,"remote_port":443,
      "transport_state":transport,"request_started_utc":"2026-10-09T09:00:00+00:00",
      "request_finished_utc":"2026-10-09T09:00:01+00:00"}

class VisibilityDiscoveryTests(unittest.TestCase):
    def test_read_only_probe_retries_transient_1042_then_accepts_exact_source(self):
        transient=response(404,{"error_code":1042})
        valid=response(200,{"authority":"P347_EXTERNAL_AUTHORITY","source_version":"sha"})
        request=Mock(side_effect=[transient,valid]); sleep=Mock()
        attempts,final,ok,error=discovery.one_probe("https://authority.workers.dev","sha","test",request,sleep)
        self.assertTrue(ok); self.assertIsNone(error); self.assertEqual(len(attempts),2)
        self.assertEqual(request.call_count,2); sleep.assert_called_once_with(2)
        self.assertEqual(final["remote_ip"],"198.51.100.20")
        self.assertEqual(request.call_args.kwargs["headers"]["X-Correlation-ID"],final["correlation_id"])

    def test_real_not_found_is_not_retried(self):
        absent=response(404,{"error":"not_found"}); request=Mock(return_value=absent)
        attempts,final,ok,error=discovery.one_probe("https://authority.workers.dev","sha","test",request,Mock())
        self.assertFalse(ok); self.assertEqual(len(attempts),1); self.assertEqual(request.call_count,1)
        self.assertEqual(final["http_status"],404)

    def test_read_only_probe_retry_budget_is_bounded(self):
        transient=response(500,{"error_code":1104}); request=Mock(return_value=transient); sleep=Mock()
        attempts,final,ok,error=discovery.one_probe("https://authority.workers.dev","sha","test",request,sleep,max_attempts=5)
        self.assertFalse(ok); self.assertEqual(len(attempts),5); self.assertEqual(request.call_count,5)
        self.assertEqual(sleep.call_count,4)

    def test_mac_only_discovery_never_admits_witness_or_lost_ack(self):
        source=Path(discovery.__file__).read_text(encoding="utf-8")
        self.assertIn('"PENDING_N100_CAPTURE_CORRELATION"',source)
        self.assertIn('"n100_packet_visibility_admitted":False',source)
        self.assertIn('"lost_ack_exercised":False',source)
        self.assertNotIn('"/v1/admin/mutate"',source)
        self.assertNotIn('"/v1/effects"',source)

    def test_cloudflare_challenge_html_is_redacted_from_public_evidence(self):
        raw='<html><head><title>Just a moment...</title></head><script>__cf_chl_tk=temporary-secret</script></html>'
        result=discovery.sanitize_result({"http_status":403,"response_body":{"raw":raw},"transport_state":"HTTP_RESPONSE_OBSERVED"})
        serialized=json.dumps(result)
        self.assertNotIn("temporary-secret",serialized)
        self.assertNotIn("__cf_chl_tk",serialized)
        self.assertTrue(result["response_body"]["cloudflare_challenge_detected"])
        self.assertTrue(result["response_body"]["raw_body_redacted"])
        self.assertEqual(len(result["response_body"]["raw_body_sha256"]),64)

if __name__=="__main__": unittest.main()
