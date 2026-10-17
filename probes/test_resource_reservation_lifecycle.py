"""Generic, public-safe resource reservation lifecycle contract probe.

This is an independent reference model. It imports no private project code and
makes no network calls or external effects.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock
from types import MappingProxyType
from typing import Mapping
from uuid import uuid4
import unittest


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    amounts: Mapping[str, int]
    state: str = "RESERVED"


class ReservationLedger:
    """Atomic in-process model for a multidimensional resource budget."""

    def __init__(self, capacity: Mapping[str, int]) -> None:
        if not capacity or any(type(v) is not int or v < 0 for v in capacity.values()):
            raise ValueError("capacity must contain non-negative integer dimensions")
        if any(not isinstance(k, str) or not k for k in capacity):
            raise ValueError("resource names must be non-empty strings")
        self._capacity = MappingProxyType(dict(capacity))
        self._used = {key: 0 for key in capacity}
        self._records: dict[str, Reservation] = {}
        self._lock = Lock()

    def reserve(self, amounts: Mapping[str, int]) -> str | None:
        request = dict(amounts)
        if not request or any(key not in self._capacity for key in request):
            raise ValueError("reservation must use known resource dimensions")
        if any(type(value) is not int or value <= 0 for value in request.values()):
            raise ValueError("reservation amounts must be positive integers")

        with self._lock:
            # Check every dimension before mutating any dimension.
            if any(self._used[key] + amount > self._capacity[key]
                   for key, amount in request.items()):
                return None
            reservation_id = uuid4().hex
            for key, amount in request.items():
                self._used[key] += amount
            self._records[reservation_id] = Reservation(
                reservation_id, MappingProxyType(dict(request))
            )
            return reservation_id

    def commit(self, reservation_id: str) -> Reservation:
        with self._lock:
            record = self._require(reservation_id)
            if record.state == "COMMITTED":
                return record
            if record.state == "RELEASED":
                raise ValueError("released reservation cannot be committed")
            committed = Reservation(record.reservation_id, record.amounts, "COMMITTED")
            self._records[reservation_id] = committed
            return committed

    def release(self, reservation_id: str) -> Reservation:
        with self._lock:
            record = self._require(reservation_id)
            if record.state == "RELEASED":
                return record
            if record.state == "COMMITTED":
                raise ValueError("committed reservation cannot be released")
            for key, amount in record.amounts.items():
                self._used[key] -= amount
            released = Reservation(record.reservation_id, record.amounts, "RELEASED")
            self._records[reservation_id] = released
            return released

    def get(self, reservation_id: str) -> Reservation:
        with self._lock:
            return self._require(reservation_id)

    def usage(self) -> Mapping[str, int]:
        with self._lock:
            return MappingProxyType(dict(self._used))

    def _require(self, reservation_id: str) -> Reservation:
        try:
            return self._records[reservation_id]
        except KeyError as exc:
            raise ValueError("unknown reservation") from exc


class ReservationLifecycleTests(unittest.TestCase):
    def test_reserve_debits_all_dimensions(self):
        ledger = ReservationLedger({"requests": 3, "tokens": 10})
        reservation_id = ledger.reserve({"requests": 1, "tokens": 4})
        self.assertIsNotNone(reservation_id)
        self.assertEqual(dict(ledger.usage()), {"requests": 1, "tokens": 4})

    def test_multidimensional_admission_is_all_or_nothing(self):
        ledger = ReservationLedger({"requests": 2, "tokens": 5})
        self.assertIsNone(ledger.reserve({"requests": 1, "tokens": 6}))
        self.assertEqual(dict(ledger.usage()), {"requests": 0, "tokens": 0})

    def test_reservation_ids_are_unique(self):
        ledger = ReservationLedger({"requests": 3})
        first = ledger.reserve({"requests": 1})
        second = ledger.reserve({"requests": 1})
        self.assertNotEqual(first, second)

    def test_release_rolls_back_only_its_own_reservation(self):
        ledger = ReservationLedger({"requests": 3, "tokens": 10})
        first = ledger.reserve({"requests": 1, "tokens": 2})
        second = ledger.reserve({"requests": 1, "tokens": 3})
        ledger.release(first)
        self.assertEqual(dict(ledger.usage()), {"requests": 1, "tokens": 3})
        third = ledger.reserve({"requests": 3, "tokens": 7})
        self.assertIsNone(third)
        self.assertEqual(ledger.get(second).state, "RESERVED")

    def test_release_is_idempotent(self):
        ledger = ReservationLedger({"requests": 1})
        reservation_id = ledger.reserve({"requests": 1})
        once = ledger.release(reservation_id)
        twice = ledger.release(reservation_id)
        self.assertEqual(once, twice)
        self.assertEqual(dict(ledger.usage()), {"requests": 0})

    def test_commit_is_idempotent_and_keeps_capacity_consumed(self):
        ledger = ReservationLedger({"requests": 1})
        reservation_id = ledger.reserve({"requests": 1})
        once = ledger.commit(reservation_id)
        twice = ledger.commit(reservation_id)
        self.assertEqual(once, twice)
        self.assertEqual(once.state, "COMMITTED")
        self.assertIsNone(ledger.reserve({"requests": 1}))

    def test_commit_and_release_are_mutually_exclusive(self):
        ledger = ReservationLedger({"requests": 2})
        committed_id = ledger.reserve({"requests": 1})
        released_id = ledger.reserve({"requests": 1})
        ledger.commit(committed_id)
        ledger.release(released_id)
        with self.assertRaisesRegex(ValueError, "cannot be released"):
            ledger.release(committed_id)
        with self.assertRaisesRegex(ValueError, "cannot be committed"):
            ledger.commit(released_id)
        self.assertEqual(dict(ledger.usage()), {"requests": 1})

    def test_unknown_reservation_fails_closed(self):
        ledger = ReservationLedger({"requests": 1})
        with self.assertRaisesRegex(ValueError, "unknown reservation"):
            ledger.commit("not-a-reservation")

    def test_caller_mutation_cannot_change_recorded_amounts(self):
        ledger = ReservationLedger({"requests": 4})
        amounts = {"requests": 2}
        reservation_id = ledger.reserve(amounts)
        amounts["requests"] = 4
        self.assertEqual(dict(ledger.get(reservation_id).amounts), {"requests": 2})
        with self.assertRaises(TypeError):
            ledger.get(reservation_id).amounts["requests"] = 3

    def test_invalid_dimension_and_amount_are_rejected_without_mutation(self):
        ledger = ReservationLedger({"requests": 3})
        with self.assertRaises(ValueError):
            ledger.reserve({"unknown": 1})
        with self.assertRaises(ValueError):
            ledger.reserve({"requests": True})
        with self.assertRaises(ValueError):
            ledger.reserve({"requests": 0})
        self.assertEqual(dict(ledger.usage()), {"requests": 0})

    def test_concurrent_admission_never_exceeds_capacity(self):
        ledger = ReservationLedger({"requests": 7})
        def attempt(_):
            return ledger.reserve({"requests": 1})
        with ThreadPoolExecutor(max_workers=32) as pool:
            results = list(pool.map(attempt, range(128)))
        admitted = [result for result in results if result is not None]
        self.assertEqual(len(admitted), 7)
        self.assertEqual(len(set(admitted)), 7)
        self.assertEqual(dict(ledger.usage()), {"requests": 7})

    def test_committed_reservation_is_not_reclaimed_by_releasing_another(self):
        ledger = ReservationLedger({"requests": 2})
        committed_id = ledger.reserve({"requests": 1})
        released_id = ledger.reserve({"requests": 1})
        ledger.commit(committed_id)
        ledger.release(released_id)
        self.assertEqual(dict(ledger.usage()), {"requests": 1})
        self.assertIsNone(ledger.reserve({"requests": 2}))


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("RESOURCE_RESERVATION_LIFECYCLE: PASS; cases=12; network=none; private_code=none")
    else:
        raise SystemExit(1)
