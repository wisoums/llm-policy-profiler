import json
from enum import StrEnum

import pytest

from llm_policy_profiler.types import PolicyType

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
