import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const workflow = fs.readFileSync(
  new URL("../../../.github/workflows/p347-external-authority-tests.yml", import.meta.url),
  "utf8",
);

test("edge and ambiguous transport retries are bounded and limited to explicitly safe requests", () => {
  assert.match(workflow, /def call\(method,path,token=None,body=None,extra=None,retry_safe=False\):/);
  assert.match(workflow, /error_code=body_json\.get\("error_code"\) if isinstance\(body_json,dict\) else None/);
  assert.match(workflow, /e\.code == 404 and error_code == 1042/);
  assert.match(workflow, /e\.code == 500 and error_code == 1104/);
  assert.match(workflow, /e\.code == 523/);
  assert.match(workflow, /if retry_safe and retryable_edge_error and attempt < 15:/);
  assert.match(workflow, /except \(URLError, TimeoutError\) as e:/);
  assert.match(workflow, /if retry_safe and attempt < 15:/);
  assert.match(workflow, /"transport_retry_events":transport_retry_events/);
  assert.match(workflow, /transport_error=False/);
  assert.match(workflow, /if not transport_error and not \\(status == 404 and error_code == 1042\\) and not \\(status == 500 and error_code == 1104\\):/);
});

test("authority mutation is not retried automatically", () => {
  assert.match(workflow, /call\("POST","\/v1\/admin\/mutate",admin,body=\{\}\)/);
  assert.doesNotMatch(workflow, /call\("POST","\/v1\/admin\/mutate",admin,body=\{\},retry_safe=True\)/);
});

test("idempotent effect operations opt into bounded safe retry", () => {
  assert.match(workflow, /call\("POST","\/v1\/effects",effect,current,h,retry_safe=True\)/);
  assert.match(workflow, /call\("GET","\/v1\/effects\/"\+eid,retry_safe=True\)/);
});
