#!/usr/bin/env python3
"""P215 bounded tenant/intent non-interference probe.

Real execution model:
- one shared runtime object;
- one shared cache and queue;
- two tenants;
- two independent intents;
- concurrent execution;
- one explicitly governed cross-branch operation;
- adversarial cross-branch reads/writes and stale authority;
- provenance reconstruction.

This is bounded executable evidence, not production multi-tenancy proof.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from hashlib import sha256
from threading import Lock


@dataclass(frozen=True)
class Scope:
    tenant: str
    intent: str
    branch: str


@dataclass(frozen=True)
class Authority:
    subject: str
    tenant: str
    intent: str
    version: int
    revoked: bool = False


class SharedRuntime:
    def __init__(self) -> None:
        self.state: dict[tuple[str, str], int] = {}
        self.cache: dict[tuple[str, str, str], str] = {}
        self.queue: list[tuple[Scope, str]] = []
        self.evidence: list[dict[str, str]] = []
        self.lock = Lock()

    def _authorized(self, authority: Authority, scope: Scope, version: int) -> bool:
        return (
            not authority.revoked
            and authority.tenant == scope.tenant
            and authority.intent == scope.intent
            and authority.version == version
        )

    def execute(
        self,
        authority: Authority,
        scope: Scope,
        version: int,
        key: str,
        value: str,
    ) -> str:
        with self.lock:
            if not self._authorized(authority, scope, version):
                raise PermissionError("cross-scope-or-stale-authority")
            state_key = (scope.tenant, scope.intent)
            self.state[state_key] = self.state.get(state_key, 0) + 1
            cache_key = (scope.tenant, scope.intent, key)
            self.cache[cache_key] = value
            self.queue.append((scope, key))
            event_id = sha256(
                f"{scope.tenant}|{scope.intent}|{scope.branch}|{key}|{value}".encode()
            ).hexdigest()
            self.evidence.append(
                {
                    "event_id": event_id,
                    "tenant": scope.tenant,
                    "intent": scope.intent,
                    "branch": scope.branch,
                    "key": key,
                }
            )
            return event_id

    def governed_cross_branch(self, source: Scope, target: Scope, key: str) -> str:
        with self.lock:
            if source.tenant != target.tenant:
                raise PermissionError("cross-tenant-interaction-not-delegated")
            marker = f"{source.branch}->{target.branch}:{key}"
            self.queue.append((target, marker))
            return marker

    def read_cache(self, scope: Scope, key: str) -> str | None:
        with self.lock:
            return self.cache.get((scope.tenant, scope.intent, key))


def main() -> None:
    runtime = SharedRuntime()
    a = Scope("tenant-a", "intent-a", "branch-a")
    b = Scope("tenant-b", "intent-b", "branch-b")
    aa = Authority("principal-a", "tenant-a", "intent-a", 1)
    bb = Authority("principal-b", "tenant-b", "intent-b", 1)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(runtime.execute, aa, a, 1, "same-name", "A"),
            pool.submit(runtime.execute, bb, b, 1, "same-name", "B"),
        ]
        ids = [f.result() for f in futures]

    assert len(set(ids)) == 2
    assert runtime.state[("tenant-a", "intent-a")] == 1
    assert runtime.state[("tenant-b", "intent-b")] == 1
    assert runtime.read_cache(a, "same-name") == "A"
    assert runtime.read_cache(b, "same-name") == "B"

    attacks = 0
    for auth, scope, version in [
        (aa, b, 1),  # cross-tenant
        (bb, a, 1),  # cross-tenant
        (aa, a, 0),  # stale
    ]:
        try:
            runtime.execute(auth, scope, version, "attack", "X")
        except PermissionError:
            attacks += 1
    assert attacks == 3

    cross = runtime.governed_cross_branch(a, Scope("tenant-a", "intent-a2", "branch-a2"), "allowed")
    assert cross == "branch-a->branch-a2:allowed"

    try:
        runtime.governed_cross_branch(a, b, "forbidden")
    except PermissionError:
        pass
    else:
        raise AssertionError("unauthorized cross-tenant interaction was accepted")

    observed = {(e["tenant"], e["intent"], e["branch"]) for e in runtime.evidence}
    assert observed == {("tenant-a", "intent-a", "branch-a"), ("tenant-b", "intent-b", "branch-b")}

    print("P215-TENANT-INTENT-FRACTAL-BOUNDARY: PASS")
    print("shared_runtime=true")
    print("shared_cache=true")
    print("shared_queue=true")
    print("concurrent_execution=true")
    print("cross_scope_attacks_rejected=3")
    print("explicit_same_tenant_cross_branch_allowed=true")
    print("cross_tenant_interaction_rejected=true")
    print("provenance_reconstructed=true")
    print("status=SUPPORTED_BOUNDED_EXECUTABLE_EVIDENCE")


if __name__ == "__main__":
    main()
