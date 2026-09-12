import dataclasses
import json
import math
from collections.abc import Callable
from enum import StrEnum
from typing import assert_type

import pytest

from llm_policy_profiler.types import PolicyResult, PolicyType

EXPECTED_MEMBERS = {
    "PRIVACY": "privacy",
    "CACHE": "cache",
    "SECURITY": "security",
    "CUSTOM": "custom",
}


def test_policy_type_is_a_str_enum() -> None:
    assert issubclass(PolicyType, StrEnum)


def test_member_set_is_exactly_the_four_v0_1_categories() -> None:
    assert {member.name for member in PolicyType} == set(EXPECTED_MEMBERS)


def test_serialized_values_are_the_stable_lowercase_names() -> None:
    assert {member.name: member.value for member in PolicyType} == EXPECTED_MEMBERS


@pytest.mark.parametrize(("name", "value"), sorted(EXPECTED_MEMBERS.items()))
def test_str_returns_the_stable_lowercase_value(name: str, value: str) -> None:
    assert str(PolicyType[name]) == value


@pytest.mark.parametrize(("name", "value"), sorted(EXPECTED_MEMBERS.items()))
def test_construction_from_a_valid_value_round_trips(name: str, value: str) -> None:
    assert PolicyType(value) is PolicyType[name]


@pytest.mark.parametrize(
    "value",
    ["Privacy", "PRIVACY", "presidio", "litellm", "", "unknown"],
)
def test_unknown_values_raise_value_error(value: str) -> None:
    with pytest.raises(ValueError, match="is not a valid PolicyType"):
        PolicyType(value)


@pytest.mark.parametrize(("name", "value"), sorted(EXPECTED_MEMBERS.items()))
def test_members_compare_and_concatenate_as_plain_strings(name: str, value: str) -> None:
    member = PolicyType[name]
    assert member == value
    assert "lpp.policy." + member == f"lpp.policy.{value}"


def test_members_serialize_to_json_without_a_custom_encoder() -> None:
    payload = {name: PolicyType[name] for name in EXPECTED_MEMBERS}
    assert json.loads(json.dumps(payload)) == EXPECTED_MEMBERS


def test_json_round_trip_restores_the_same_members() -> None:
    encoded = json.dumps(list(PolicyType))
    assert [PolicyType(value) for value in json.loads(encoded)] == list(PolicyType)


SENSITIVE_OUTPUT = "CANARY-SSN-123-45-6789-DO-NOT-LOG"


def make_result(
    output: str = "anonymized text",
    *,
    policy_type: PolicyType = PolicyType.PRIVACY,
    policy_name: str = "pii_redaction",
    duration_seconds: float = 0.0123,
) -> PolicyResult[str]:
    return PolicyResult(
        output=output,
        policy_type=policy_type,
        policy_name=policy_name,
        duration_seconds=duration_seconds,
    )


def test_construction_retains_every_field_exactly() -> None:
    result = make_result()

    assert result.output == "anonymized text"
    assert result.policy_type is PolicyType.PRIVACY
    assert result.policy_name == "pii_redaction"
    assert result.duration_seconds == 0.0123


def test_output_preserves_the_exact_object_identity() -> None:
    payload = {"entities": ["PERSON"]}
    result: PolicyResult[dict[str, list[str]]] = PolicyResult(
        output=payload,
        policy_type=PolicyType.PRIVACY,
        policy_name="pii_redaction",
        duration_seconds=0.5,
    )

    assert result.output is payload


def test_generic_parameter_preserves_the_output_type() -> None:
    result: PolicyResult[list[int]] = PolicyResult(
        output=[1, 2, 3],
        policy_type=PolicyType.CACHE,
        policy_name="semantic_cache",
        duration_seconds=0.25,
    )

    assert_type(result.output, list[int])
    assert result.output == [1, 2, 3]


def test_core_fields_are_exactly_the_four_defined_by_the_contract() -> None:
    fields = dataclasses.fields(make_result())

    assert [f.name for f in fields] == [
        "output",
        "policy_type",
        "policy_name",
        "duration_seconds",
    ]


def test_positional_construction_is_rejected() -> None:
    untyped_constructor: Callable[..., PolicyResult[str]] = PolicyResult

    with pytest.raises(TypeError):
        untyped_constructor("out", PolicyType.PRIVACY, "pii_redaction", 0.1)


def test_instances_are_frozen() -> None:
    result = make_result()

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.policy_name = "renamed"  # type: ignore[misc]

    assert result.policy_name == "pii_redaction"


def test_instances_are_slotted_and_expose_no_writable_dict() -> None:
    result = make_result()

    assert PolicyResult.__slots__ == ("output", "policy_type", "policy_name", "duration_seconds")
    assert not hasattr(result, "__dict__")


def test_extra_attributes_cannot_be_attached() -> None:
    result = make_result()

    # A frozen+slotted dataclass rejects unknown attributes, but the exception type
    # is a CPython implementation detail: `slots=True` rebuilds the class, so the
    # generated `__setattr__` closes over a stale class and its `super()` call raises
    # TypeError instead of the AttributeError a plain slotted class would raise.
    with pytest.raises((AttributeError, TypeError)):
        result.prompt = SENSITIVE_OUTPUT  # type: ignore[attr-defined]


def test_repr_excludes_the_output_but_keeps_safe_metadata() -> None:
    result = make_result(SENSITIVE_OUTPUT)
    rendered = repr(result)

    assert SENSITIVE_OUTPUT not in rendered
    assert "output" not in rendered
    assert "pii_redaction" in rendered
    assert "privacy" in rendered
    assert "0.0123" in rendered


def test_zero_duration_is_valid() -> None:
    assert make_result(duration_seconds=0.0).duration_seconds == 0.0


def test_negative_duration_raises_value_error() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        make_result(duration_seconds=-0.001)


@pytest.mark.parametrize("duration", [math.nan, math.inf, -math.inf])
def test_non_finite_duration_raises_value_error(duration: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        make_result(duration_seconds=duration)


@pytest.mark.parametrize("duration", [True, False])
def test_boolean_duration_raises_value_error(duration: bool) -> None:
    # `bool` subclasses `int`, so True/False satisfy math.isfinite() and `>= 0`.
    with pytest.raises(ValueError, match="not bool"):
        make_result(duration_seconds=duration)


@pytest.mark.parametrize("policy_name", ["", " ", "\t", "\n", "   \t\n "])
def test_empty_or_whitespace_policy_name_raises_value_error(policy_name: str) -> None:
    with pytest.raises(ValueError, match="policy_name"):
        make_result(policy_name=policy_name)


@pytest.mark.parametrize(
    "policy_name",
    ["  pii_redaction  ", "PII Redaction v2", "team/policy name", "\tcache lookup\n"],
)
def test_valid_policy_names_are_preserved_verbatim(policy_name: str) -> None:
    assert make_result(policy_name=policy_name).policy_name == policy_name


@pytest.mark.parametrize("policy_type", list(PolicyType))
def test_every_policy_type_is_accepted(policy_type: PolicyType) -> None:
    assert make_result(policy_type=policy_type).policy_type is policy_type
