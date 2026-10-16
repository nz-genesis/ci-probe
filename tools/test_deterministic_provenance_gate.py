#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from deterministic_provenance_gate import verify


class ProvenanceGateTests(unittest.TestCase):
    def make_case(self):
        root = Path(tempfile.mkdtemp())
        corpus = root / "corpus"
        corpus.mkdir()
        source = corpus / "source.txt"
        source.write_text("one\ntwo\n", encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({"schema":"generic-provenance-v1","sources":[{"source_id":"S","path":"source.txt","sha256":digest}]}), encoding="utf-8")
        claims = root / "claims.jsonl"
        claims.write_text(json.dumps({"claim_id":"C","source_id":"S","start_line":1,"end_line":2,"exact_span":"one\ntwo\n","claim":"two lines"}) + "\n", encoding="utf-8")
        return root, corpus, manifest, claims

    def test_baseline_passes(self):
        _, corpus, manifest, claims = self.make_case()
        self.assertEqual(verify(manifest, claims, corpus)["status"], "PASS")

    def test_source_tamper_fails(self):
        _, corpus, manifest, claims = self.make_case()
        (corpus / "source.txt").write_text("one\nTWO\n", encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")

    def test_exact_span_tamper_fails(self):
        _, corpus, manifest, claims = self.make_case()
        claims.write_text(json.dumps({"claim_id":"C","source_id":"S","start_line":1,"end_line":2,"exact_span":"one\nTWO\n","claim":"two lines"}) + "\n", encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")

    def test_unknown_source_fails(self):
        _, corpus, manifest, claims = self.make_case()
        claims.write_text(json.dumps({"claim_id":"C","source_id":"UNKNOWN","start_line":1,"end_line":1,"exact_span":"one\n","claim":"one"}) + "\n", encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")

    def test_path_escape_fails(self):
        _, corpus, manifest, claims = self.make_case()
        outside = corpus.parent / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        digest = hashlib.sha256(outside.read_bytes()).hexdigest()
        manifest.write_text(json.dumps({"schema":"generic-provenance-v1","sources":[{"source_id":"S","path":"../outside.txt","sha256":digest}]}), encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")

    def test_malformed_manifest_fails_closed(self):
        _, corpus, manifest, claims = self.make_case()
        manifest.write_text("{", encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")

    def test_malformed_claims_fails_closed(self):
        _, corpus, manifest, claims = self.make_case()
        claims.write_text("{", encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")

    def test_duplicate_claim_id_fails(self):
        _, corpus, manifest, claims = self.make_case()
        row = {"claim_id":"C","source_id":"S","start_line":1,"end_line":1,"exact_span":"one\n","claim":"one"}
        claims.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")

    def test_invalid_utf8_fails_closed(self):
        _, corpus, manifest, claims = self.make_case()
        source = corpus / "source.txt"
        source.write_bytes(b"one\n\xff\n")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        manifest.write_text(json.dumps({"schema":"generic-provenance-v1","sources":[{"source_id":"S","path":"source.txt","sha256":digest}]}), encoding="utf-8")
        self.assertEqual(verify(manifest, claims, corpus)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
