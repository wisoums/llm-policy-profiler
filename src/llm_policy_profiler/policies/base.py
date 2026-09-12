"""Vendor-neutral structural contract describing what a policy *is*."""

from typing import Protocol

from llm_policy_profiler.types import PolicyType

__all__ = ["Policy"]


class Policy(Protocol):
    """Identity of a policy the profiler can measure.

    This contract covers identity only: a conforming object says what it is called
    and which bounded family it belongs to, and nothing more. Deliberately absent is
    any execution method — no ``apply``, ``execute``, ``run``, ``lookup``,
    ``evaluate``, or ``__call__`` — because policy families do not share one natural
    operation. A privacy adapter anonymizes, a cache adapter looks up, a security
    adapter evaluates; forcing those into a single inherited method name would make
    the core abstraction lie about every adapter after the first.

    Conformance is structural, so an implementation never imports or inherits from
    ``Policy``; it simply exposes the two members::

        class PiiRedaction:
            name = "pii_redaction"
            policy_type = PolicyType.PRIVACY

    Both members are declared as read-only properties. That admits implementations
    backed by plain instance attributes *and* by ``@property`` accessors, while
    leaving callers no license to reassign a policy's identity through a ``Policy``
    reference.

    The protocol is intentionally **not** ``@runtime_checkable``:
    ``isinstance(obj, Policy)`` would only confirm that two attributes exist, not
    that they hold a ``str`` and a ``PolicyType``, which is a weaker guarantee than
    the contract states. Conformance is proven by a type checker instead.

    Values are not validated here — a protocol is a typing contract, not a value
    object. Runtime invariants belong where measurements are constructed, such as
    :class:`~llm_policy_profiler.types.PolicyResult`.
    """

    @property
    def name(self) -> str:
        """Name of the concrete logical policy, such as ``"semantic_cache"``."""
        ...

    @property
    def policy_type(self) -> PolicyType:
        """Bounded high-level family this policy belongs to."""
        ...
