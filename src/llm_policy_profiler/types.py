"""Core, vendor-neutral data types shared by the policy profiler."""

from enum import StrEnum

__all__ = ["PolicyType"]


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
