from dataclasses import dataclass
from typing import assert_type

import pytest

import llm_policy_profiler.policies as policies_package
from llm_policy_profiler.policies import Policy
from llm_policy_profiler.policies.base import Policy as PolicyFromBaseModule
from llm_policy_profiler.types import PolicyType


class AttributePolicy:
    """Conforms through ordinary instance attributes, without inheriting Policy."""

    def __init__(self, name: str, policy_type: PolicyType) -> None:
        self.name = name
        self.policy_type = policy_type


class PropertyPolicy:
    """Conforms through read-only property accessors, without inheriting Policy."""

    def __init__(self, name: str, policy_type: PolicyType) -> None:
        self._name = name
        self._policy_type = policy_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def policy_type(self) -> PolicyType:
        return self._policy_type


class ClassVarPolicy:
    """Metadata only: no apply/execute/run/lookup/evaluate/__call__ anywhere."""

    name = "pii_redaction"
    policy_type = PolicyType.PRIVACY


@dataclass(frozen=True)
class DataclassPolicy:
    """A frozen dataclass conforms without any protocol-specific machinery."""

    name: str
    policy_type: PolicyType


def identify(policy: Policy) -> tuple[str, PolicyType]:
    """Accept anything that structurally satisfies the protocol."""
    return policy.name, policy.policy_type


CONFORMING_POLICIES: list[Policy] = [
    AttributePolicy("pii_redaction", PolicyType.PRIVACY),
    PropertyPolicy("semantic_cache", PolicyType.CACHE),
    ClassVarPolicy(),
    DataclassPolicy(name="prompt_injection_scan", policy_type=PolicyType.SECURITY),
]


@pytest.mark.parametrize("policy", CONFORMING_POLICIES)
def test_structural_implementations_are_accepted_as_policies(policy: Policy) -> None:
    name, policy_type = identify(policy)

    assert isinstance(name, str)
    assert isinstance(policy_type, PolicyType)


def test_instance_attribute_implementation_conforms() -> None:
    policy = AttributePolicy("pii_redaction", PolicyType.PRIVACY)

    assert identify(policy) == ("pii_redaction", PolicyType.PRIVACY)


def test_property_implementation_conforms() -> None:
    policy = PropertyPolicy("semantic_cache", PolicyType.CACHE)

    assert identify(policy) == ("semantic_cache", PolicyType.CACHE)


def test_metadata_only_implementation_needs_no_execution_method() -> None:
    policy = ClassVarPolicy()

    for forbidden in ("apply", "execute", "run", "lookup", "evaluate", "__call__"):
        assert not hasattr(policy, forbidden)

    assert identify(policy) == ("pii_redaction", PolicyType.PRIVACY)


def test_the_protocol_declares_exactly_two_read_only_properties() -> None:
    declared = {name: member for name, member in vars(Policy).items() if not name.startswith("_")}

    assert set(declared) == {"name", "policy_type"}
    for member in declared.values():
        assert isinstance(member, property)
        assert member.fset is None
        assert member.fdel is None


def test_the_protocol_declares_no_execution_method() -> None:
    # `hasattr` would be useless here: every class object is callable via
    # `type.__call__`, so only the protocol's own namespace answers this.
    for forbidden in ("apply", "execute", "run", "lookup", "evaluate", "__call__"):
        assert forbidden not in vars(Policy)


def test_conformance_requires_no_inheritance() -> None:
    for implementation in (AttributePolicy, PropertyPolicy, ClassVarPolicy, DataclassPolicy):
        assert implementation.__bases__ == (object,)


def test_typed_access_preserves_the_declared_member_types() -> None:
    policy: Policy = DataclassPolicy(name="semantic_cache", policy_type=PolicyType.CACHE)

    assert_type(policy.name, str)
    assert_type(policy.policy_type, PolicyType)
    assert policy.name == "semantic_cache"
    assert policy.policy_type is PolicyType.CACHE


def test_policy_is_re_exported_from_the_policies_package() -> None:
    assert Policy is PolicyFromBaseModule
    assert policies_package.__all__ == ["Policy"]


def test_protocol_is_static_only_and_not_runtime_checkable() -> None:
    policy = ClassVarPolicy()

    # A non-runtime-checkable Protocol rejects isinstance() outright; LPP proves
    # conformance with a type checker rather than at runtime.
    with pytest.raises(TypeError):
        isinstance(policy, Policy)  # type: ignore[misc]


def test_protocol_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Policy()  # type: ignore[misc]
