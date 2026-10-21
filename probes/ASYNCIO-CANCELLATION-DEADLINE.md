# Generic asyncio cancellation and shutdown-deadline probe

**Status:** ACTIVE GENERIC PROBE  
**Scope:** Python standard-library task cancellation and waiting semantics  
**Runtime:** Python 3.14.7 in the dedicated workflow

## Question

Does `asyncio.wait_for(task, timeout=...)` impose a hard upper bound when the
target task suppresses cancellation? Can `asyncio.wait(..., timeout=...)`
provide a bounded observation period without cancelling the target task? What
happens when the waiter itself is cancelled?

## Execution

The companion script runs three deterministic event-controlled experiments:

1. `wait_for` timeout against a worker that catches cancellation and waits for
   explicit release;
2. bounded `wait` against a still-live cancellation-resistant worker;
3. cancellation of the task waiting in `asyncio.wait`, observing whether the
   target worker remains unaffected.

No external services, third-party packages, secrets, provider sessions or
private source are used.

## Evidence boundary

A successful workflow proves only the observed Python standard-library
behavior for the exact Python version and run. It does not prove any private
application's shutdown implementation, Browser/Ledger safety, or real
browser/provider integration. The owning private implementation still requires
tests against its actual code.

## Acceptance output

The script emits separate result lines for all three semantics and ends with
`PROBE_RESULT=PASS` only if all assertions hold.
