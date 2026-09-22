"""UUIDv7 identifiers, implemented here rather than assumed to exist.

Every IACode entity uses one identifier strategy: UUID version 7 as defined by RFC 9562. A v7
identifier carries a millisecond Unix timestamp in its 48 most significant bits, which makes a
primary key that is globally unique *and* ordered by creation time. That ordering is why the
strategy was chosen: a random v4 key scatters index inserts across the B-tree, and every table this
Gate creates is expected to grow monotonically.

The implementation is standard-library only and deliberate:

- Python 3.13 has no ``uuid.uuid7``; it arrives in 3.14. Depending on it would pin the runtime to a
  version this Gate does not require.
- The third-party alternatives are native extensions. Adding a compiled dependency to obtain
  sixteen bytes is a build and supply-chain cost with no engineering return.

Monotonicity within a millisecond is the part a naive implementation gets wrong. RFC 9562 method 3
is used: the 12-bit ``rand_a`` field is a sub-millisecond counter that increments while the
timestamp does not move, so two identifiers generated in the same millisecond still sort in
generation order. When the counter would overflow, generation waits for the next millisecond rather
than emitting an out-of-order value.
"""

from __future__ import annotations

import os
import threading
import time
import uuid

__all__ = ["uuid7", "uuid7_timestamp_ms"]

# Bits 48..59 of a v7 identifier. RFC 9562 allows this field to carry a monotonic counter when the
# generator needs ordering inside a single millisecond.
_COUNTER_BITS = 12
_COUNTER_MAX = (1 << _COUNTER_BITS) - 1

_lock = threading.Lock()
_last_timestamp_ms = -1
_counter = 0


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def uuid7() -> uuid.UUID:
    """A new, time-ordered UUID version 7.

    Thread safe: the timestamp and the intra-millisecond counter are advanced under a lock, so two
    threads cannot observe the same counter value for the same millisecond.
    """
    global _last_timestamp_ms, _counter

    with _lock:
        timestamp_ms = _now_ms()
        if timestamp_ms > _last_timestamp_ms:
            _last_timestamp_ms = timestamp_ms
            _counter = 0
        elif timestamp_ms == _last_timestamp_ms:
            if _counter >= _COUNTER_MAX:
                # Waiting is the only correct answer: emitting a wrapped counter would produce an
                # identifier that sorts before one generated earlier.
                while timestamp_ms <= _last_timestamp_ms:
                    time.sleep(0.0002)
                    timestamp_ms = _now_ms()
                _last_timestamp_ms = timestamp_ms
                _counter = 0
            else:
                _counter += 1
        else:
            # The clock moved backwards. Keeping the last observed millisecond preserves ordering
            # at the cost of a timestamp that is briefly ahead of the wall clock, which is the
            # trade RFC 9562 recommends for a monotonic generator.
            timestamp_ms = _last_timestamp_ms
            if _counter >= _COUNTER_MAX:
                _last_timestamp_ms += 1
                timestamp_ms = _last_timestamp_ms
                _counter = 0
            else:
                _counter += 1
        counter = _counter

    value = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
    value |= 0x7 << 76
    value |= (counter & _COUNTER_MAX) << 64
    value |= 0b10 << 62
    value |= int.from_bytes(os.urandom(8), "big") & ((1 << 62) - 1)
    return uuid.UUID(int=value)


def uuid7_timestamp_ms(value: uuid.UUID) -> int:
    """The millisecond Unix timestamp embedded in a v7 identifier."""
    if value.version != 7:
        raise ValueError(f"not a UUID version 7: {value}")
    return value.int >> 80
