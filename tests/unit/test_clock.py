from typing import assert_type

import pytest

import llm_policy_profiler.clock as clock_module
from llm_policy_profiler.clock import Clock

WALL_CLOCK_MEMBERS = (
    "now",
    "utcnow",
    "today",
    "time",
    "timestamp",
    "datetime",
    "date",
    "timezone",
    "tzinfo",
    "sleep",
    "advance",
    "reset",
    "set",
)


class CountingClock:
    """Conforms structurally without inheriting Clock, and without sleeping."""

    def __init__(self, readings: list[float]) -> None:
        self._readings = readings
        self.calls = 0

    def monotonic(self) -> float:
        reading = self._readings[self.calls]
        self.calls += 1
        return reading


class ConstantClock:
    """A clock that never advances is still a valid Clock."""

    def monotonic(self) -> float:
        return 0.0


def elapsed_seconds(clock: Clock) -> float:
    """Accept any structural Clock and measure across two readings."""
    start = clock.monotonic()
    return clock.monotonic() - start


def test_structural_implementation_is_accepted_where_clock_is_expected() -> None:
    clock = CountingClock([10.0, 10.25])

    assert elapsed_seconds(clock) == 0.25
    assert clock.calls == 2


def test_conformance_requires_no_inheritance() -> None:
    for implementation in (CountingClock, ConstantClock):
        assert implementation.__bases__ == (object,)


def test_a_clock_that_does_not_advance_still_conforms() -> None:
    assert elapsed_seconds(ConstantClock()) == 0.0


def test_typed_access_preserves_the_float_return_type() -> None:
    clock: Clock = CountingClock([3.5])

    reading = clock.monotonic()

    assert_type(reading, float)
    assert reading == 3.5


def test_only_differences_between_readings_are_used() -> None:
    # The absolute origin carries no meaning: two clocks with wildly different
    # origins report the same elapsed duration.
    near_zero = CountingClock([0.0, 1.5])
    far_future = CountingClock([1_000_000.0, 1_000_001.5])

    assert elapsed_seconds(near_zero) == elapsed_seconds(far_future) == 1.5


def test_the_protocol_declares_exactly_one_public_operation() -> None:
    declared = [name for name in vars(Clock) if not name.startswith("_")]

    assert declared == ["monotonic"]


def test_the_protocol_declares_no_wall_clock_or_mutation_member() -> None:
    for forbidden in WALL_CLOCK_MEMBERS:
        assert forbidden not in vars(Clock)


def test_implementations_need_no_wall_clock_member() -> None:
    clock = ConstantClock()

    for forbidden in WALL_CLOCK_MEMBERS:
        assert not hasattr(clock, forbidden)

    assert elapsed_seconds(clock) == 0.0


def test_the_clock_module_reads_no_real_clock_on_import() -> None:
    # A pure contract module: importing it must not pull in a time source, so it
    # cannot take a reading or sleep as a side effect of import.
    assert "time" not in vars(clock_module)
    assert clock_module.__all__ == ["Clock"]


def test_protocol_is_static_only_and_not_runtime_checkable() -> None:
    # A non-runtime-checkable Protocol rejects isinstance() outright; conformance
    # is proven by the type checker instead.
    with pytest.raises(TypeError):
        isinstance(ConstantClock(), Clock)  # type: ignore[misc]


def test_protocol_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Clock()  # type: ignore[misc]
