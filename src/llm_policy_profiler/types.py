"""Core, vendor-neutral data types shared by the policy profiler."""

import math
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, TypeVar

__all__ = ["PolicyResult", "PolicyType"]

T = TypeVar("T")


class PolicyType(StrEnum):
    """High-level family a policy belongs to.

    A member identifies *what kind of concern* a policy addresses (privacy, cache,
    security, or something else), never the concrete implementation or vendor behind
    it. There is deliberately no ``PRESIDIO``, ``LITELLM``, or ``REDIS`` member: the
    enum stays closed and low-cardinality so it is safe to use as a typed API value
    and as an OpenTelemetry attribute.

    The lowercase string values are the stable serialization form used in JSON,
    reports, and telemetry:

    >>> str(PolicyType.PRIVACY)
    'privacy'
    >>> PolicyType("cache") is PolicyType.CACHE
    True

    Unknown values raise :class:`ValueError`; there is no silent fallback. Use
    :attr:`CUSTOM` for policy families outside the built-in categories.
    """

    PRIVACY = "privacy"
    CACHE = "cache"
    SECURITY = "security"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True, kw_only=True)
class PolicyResult(Generic[T]):
    """Outcome of one successfully completed profiled policy execution.

    The result carries the policy's own output together with the bounded metadata
    the profiler measured about it. Returning a ``PolicyResult`` *is* the success
    signal: there is no status, error, or exception field, so an instance can never
    describe a half-failed execution.

    Construction is keyword-only, frozen, and slotted, so a completed measurement
    cannot be mutated or decorated with extra attributes after the fact::

        PolicyResult(
            output=anonymized_prompt,
            policy_type=PolicyType.PRIVACY,
            policy_name="pii_redaction",
            duration_seconds=0.0123,
        )

    Args:
        output: Whatever the policy produced, preserved exactly as given. It may
            contain prompts, responses, or PII, so it is excluded from the default
            ``repr()``; it is never copied, redacted, or otherwise transformed.
        policy_type: Bounded high-level family the policy belongs to.
        policy_name: Name of the concrete logical policy, such as
            ``"pii_redaction"``. Must contain at least one non-whitespace
            character and is stored exactly as provided.
        duration_seconds: Elapsed duration in seconds. Must be finite
            and non-negative; zero is valid. Booleans are rejected even though
            ``bool`` subclasses ``int``.

    Raises:
        ValueError: If ``policy_name`` is empty or whitespace-only, or if
            ``duration_seconds`` is a ``bool``, negative, ``NaN``, or infinite.
    """

    output: T = field(repr=False)
    policy_type: PolicyType
    policy_name: str
    duration_seconds: float

    def __post_init__(self) -> None:
        if not self.policy_name.strip():
            raise ValueError("policy_name must not be empty or whitespace-only")
        # `bool` subclasses `int`, so True/False would otherwise pass both the
        # finiteness and sign checks and be stored as a boolean duration.
        if isinstance(self.duration_seconds, bool):
            raise ValueError(
                f"duration_seconds must be a real number, not bool, got {self.duration_seconds!r}"
            )
        if not math.isfinite(self.duration_seconds):
            raise ValueError(f"duration_seconds must be finite, got {self.duration_seconds!r}")
        if self.duration_seconds < 0:
            raise ValueError(
                f"duration_seconds must be non-negative, got {self.duration_seconds!r}"
            )
