import json, subprocess, unittest
from pathlib import Path
from unittest.mock import patch
import actor

class MacActorContractTests(unittest.TestCase):
    def test_fingerprint_is_canonical_and_payload_sensitive(self):
        a={"generation":2,"payload":{"amount":1}}
        b={"payload":{"amount":1},"generation":2}
        c={"generation":2,"payload":{"amount":2}}
        self.assertEqual(actor.fingerprint(a),actor.fingerprint(b))
        self.assertNotEqual(actor.fingerprint(a),actor.fingerprint(c))
        self.assertEqual(len(actor.fingerprint(a)),64)

    def test_observed_response_preserves_actual_peer(self):
        raw='{"effect_id":"e1"}\n'+actor.META+"201\t192.0.2.10\t198.51.100.20\t443\t0.125\n"
        r=actor.parse_curl(raw,"",0)
        self.assertEqual(r["http_status"],201)
        self.assertEqual(r["transport_state"],"HTTP_RESPONSE_OBSERVED")
        self.assertEqual(r["local_ip"],"192.0.2.10")
        self.assertEqual(r["remote_ip"],"198.51.100.20")

    def test_timeout_000_is_unknown_but_keeps_peer(self):
        raw='{"partial":true}\n'+actor.META+"000\t192.0.2.10\t198.51.100.20\t443\t3.001\n"
        r=actor.parse_curl(raw,"Operation timed out",28)
        self.assertIsNone(r["http_status"])
        self.assertEqual(r["transport_state"],"UNKNOWN")
        self.assertEqual(r["remote_ip"],"198.51.100.20")

    def test_missing_metadata_is_unknown(self):
        r=actor.parse_curl("","Could not connect",7)
        self.assertIsNone(r["http_status"])
        self.assertEqual(r["transport_state"],"UNKNOWN")

    def test_effect_call_is_single_attempt_and_does_not_leak_token(self):
        token="do-not-leak-this-token"
        done=subprocess.CompletedProcess(args=["curl"],returncode=28,
            stdout=actor.META+"000\t192.0.2.10\t198.51.100.20\t443\t3.0\n",stderr="timeout")
        with patch("actor.subprocess.run",return_value=done) as run:
            result=actor.request("https://authority.example/v1/effects","POST",token,
                {"generation":2,"payload":{"amount":1}},{"Idempotency-Key":"e1"},3)
        self.assertEqual(run.call_count,1)
        command=run.call_args.args[0]
        self.assertNotIn(token," ".join(command))
        auth_ref=next(v[1:] for v in command if v.startswith("@"))
        self.assertFalse(Path(auth_ref).exists())
        self.assertEqual(result["transport_state"],"UNKNOWN")
        self.assertNotIn(token,json.dumps(result))
        self.assertNotIn("authorization",json.dumps(result).lower())

    def test_http_500_is_observed_response_not_unknown(self):
        raw='{"error":"server_error"}\n'+actor.META+"500\t192.0.2.10\t198.51.100.20\t443\t0.01\n"
        r=actor.parse_curl(raw,"",0)
        self.assertEqual(r["http_status"],500)
        self.assertEqual(r["transport_state"],"HTTP_RESPONSE_OBSERVED")

    def test_actor_does_not_activate_fault_injector(self):
        source=Path(actor.__file__).read_text(encoding="utf-8")
        self.assertIn('"owned_by_actor":False',source)
        self.assertIn('"activated_by_actor":False',source)
        self.assertNotIn("pfctl",source)
        self.assertNotIn("iptables",source)

    def test_actor_recovery_does_not_claim_physical_lost_ack(self):
        source=Path(actor.__file__).read_text(encoding="utf-8")
        self.assertIn('unknown and present and retry_ok',source)
        self.assertIn('run["claims"]["lost_ack_exercised"]=False',source)
        self.assertIn('"ambiguous_effect_recovery_verified":False',source)
        self.assertIn('"physical_effect_admitted":False',source)
        self.assertIn('"independent_witness_admitted":False',source)

if __name__=="__main__": unittest.main()
