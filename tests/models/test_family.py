import pytest
from pydantic import ValidationError

from housepy.models.event import Event
from housepy.models.family import Family


def test_defaults():
    family = Family("test.family")
    assert family.father is None
    assert family.mother is None
    assert family.children == []
    assert family.married is None
    assert family.divorced is None


def test_children_default_is_not_shared_between_instances():
    first = Family("test.family-1")
    second = Family("test.family-2")
    first.children.append("test.child")  # type: ignore[attr-defined]
    assert second.children == []


def test_full_fields_round_trip():
    family = Family(
        "test.father+test.mother+family-1",
        father="test.father",
        mother="test.mother",
        children=["test.child-1", "test.child-2"],
        married=Event(1741, 8, 12),
        divorced=Event(1755, 1, 1),
    )
    assert family.father == "test.father"
    assert family.mother == "test.mother"
    assert family.children == ["test.child-1", "test.child-2"]
    assert family.married == Event(1741, 8, 12)
    assert family.divorced == Event(1755, 1, 1)


def test_missing_required_slug_raises_validation_error():
    with pytest.raises(ValidationError):
        Family()  # type: ignore[call-arg]
