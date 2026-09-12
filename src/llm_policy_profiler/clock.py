"""Injectable monotonic time source used to measure elapsed durations."""

from typing import Protocol

__all__ = ["Clock"]


class Clock(Protocol):
    """A monotonic time source the profiler can measure elapsed durations against.

    The whole contract is one reading. Elapsed time is always the difference
    between two readings taken from the *same* clock instance::

        start = clock.monotonic()
        ...
        elapsed_seconds = clock.monotonic() - start

    Injecting this dependency is what keeps timing deterministic: production code
    can supply the system monotonic clock while tests supply a clock they step
    forward explicitly, so no test has to sleep or trust machine scheduling.

    Deliberately absent are ``now()``, ``utcnow()``, ``sleep()``, ``advance()``,
    and every datetime/timezone accessor. Wall-clock time can jump forward or
    backward under NTP correction, manual changes, or daylight-saving shifts, which
    makes it unfit for duration math; excluding it from the contract means no
    implementation can offer it as a substitute. Stepping time forward belongs to a
    fake clock, not to the interface every production clock must satisfy.

    Conformance is structural, so an implementation never imports or inherits from
    ``Clock``; defining the one method is enough::

        class CountingClock:
            def monotonic(self) -> float:
                return 1.5

    The protocol is intentionally not ``@runtime_checkable``: the presence of a
    ``monotonic`` attribute says nothing about its signature or return type, which
    is a weaker guarantee than this contract states. A type checker proves
    conformance instead.
    """

    def monotonic(self) -> float:
        """Return the current monotonic reading, in seconds.

        Only differences between readings carry meaning. The absolute value has no
        application meaning and is not a timestamp: it cannot be converted to a
        date, a time of day, or an epoch offset, and readings from two different
        clock instances must never be subtracted from one another.
        """
        ...
