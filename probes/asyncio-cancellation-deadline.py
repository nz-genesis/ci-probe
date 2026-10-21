"""Public-safe probe of Python asyncio cancellation and timeout semantics.

This exercises only the Python standard library. It does not import or model
any private application implementation. A passing run proves only the observed
asyncio behavior for the Python version printed by this script.
"""
import asyncio
import sys

RESULT = "worker-returned-after-suppressing-cancellation"


async def cancellation_resistant_worker(started, cancellation_seen, release, finished):
    started.set()
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        cancellation_seen.set()
        while not release.is_set():
            try:
                await release.wait()
            except asyncio.CancelledError:
                continue
    finally:
        finished.set()
    return RESULT


async def probe_wait_for_timeout_is_not_a_hard_deadline():
    started = asyncio.Event()
    cancellation_seen = asyncio.Event()
    release = asyncio.Event()
    finished = asyncio.Event()
    worker = asyncio.create_task(
        cancellation_resistant_worker(started, cancellation_seen, release, finished)
    )
    await asyncio.wait_for(started.wait(), timeout=1)

    async def release_after_observing_cancellation():
        await asyncio.wait_for(cancellation_seen.wait(), timeout=1)
        await asyncio.sleep(0.05)
        release.set()

    releaser = asyncio.create_task(release_after_observing_cancellation())
    loop = asyncio.get_running_loop()
    before = loop.time()
    outcome = "returned"
    result = None
    try:
        result = await asyncio.wait_for(worker, timeout=0.01)
    except TimeoutError:
        outcome = "timeout-error"
    elapsed = loop.time() - before
    await asyncio.wait_for(releaser, timeout=1)

    assert elapsed >= 0.04, (
        f"wait_for() did not expose expected cancellation-wait overrun: {elapsed:.4f}s"
    )
    assert worker.done() and finished.is_set(), "worker was not observed finished"
    if outcome == "returned":
        assert result == RESULT
    print(
        "WAIT_FOR_TIMEOUT_OVERRUN=OBSERVED "
        f"outcome={outcome} elapsed_seconds={elapsed:.4f}"
    )


async def probe_wait_timeout_preserves_live_task():
    started = asyncio.Event()
    cancellation_seen = asyncio.Event()
    release = asyncio.Event()
    finished = asyncio.Event()
    worker = asyncio.create_task(
        cancellation_resistant_worker(started, cancellation_seen, release, finished)
    )
    await asyncio.wait_for(started.wait(), timeout=1)
    worker.cancel()
    await asyncio.wait_for(cancellation_seen.wait(), timeout=1)

    loop = asyncio.get_running_loop()
    before = loop.time()
    done, pending = await asyncio.wait({worker}, timeout=0.05)
    elapsed = loop.time() - before

    assert worker in pending and worker not in done, (
        "wait() did not return with live worker pending"
    )
    assert not worker.done() and not finished.is_set(), (
        "worker unexpectedly finished before explicit release"
    )
    assert elapsed < 0.5, (
        f"wait() exceeded its bounded wait unexpectedly: {elapsed:.4f}s"
    )

    release.set()
    result = await asyncio.wait_for(worker, timeout=1)
    assert result == RESULT and finished.is_set()
    print(
        "ASYNCIO_WAIT_BOUNDED=PASS "
        f"elapsed_seconds={elapsed:.4f} worker_preserved=True"
    )


async def probe_cancelling_waiter_does_not_cancel_worker():
    started = asyncio.Event()
    cancellation_seen = asyncio.Event()
    release = asyncio.Event()
    finished = asyncio.Event()
    worker = asyncio.create_task(
        cancellation_resistant_worker(started, cancellation_seen, release, finished)
    )
    await asyncio.wait_for(started.wait(), timeout=1)

    waiter = asyncio.create_task(asyncio.wait({worker}, timeout=5))
    await asyncio.sleep(0)
    waiter.cancel()
    try:
        await waiter
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("cancelled wait() waiter did not propagate its cancellation")

    assert not worker.done(), "cancelling wait() unexpectedly cancelled the worker"
    assert worker.cancelling() == 0, "wait() forwarded cancellation to the worker"
    assert not cancellation_seen.is_set(), "worker received unexpected cancellation"

    worker.cancel()
    await asyncio.wait_for(cancellation_seen.wait(), timeout=1)
    release.set()
    result = await asyncio.wait_for(worker, timeout=1)
    assert result == RESULT and finished.is_set()
    print("ASYNCIO_WAIT_WAITER_CANCEL=PASS worker_preserved=True")


async def main():
    await probe_wait_for_timeout_is_not_a_hard_deadline()
    await probe_wait_timeout_preserves_live_task()
    await probe_cancelling_waiter_does_not_cancel_worker()
    print(f"PROBE_RESULT=PASS python={sys.version.split()[0]}")


if __name__ == "__main__":
    asyncio.run(main())
