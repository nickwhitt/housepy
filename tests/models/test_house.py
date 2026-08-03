import pytest
from pydantic import ValidationError

from housepy.models.event import Event
from housepy.models.house import House


def test_str_returns_name():
    house = House("hesse-darmstadt", "Hesse-Darmstadt")
    assert str(house) == "Hesse-Darmstadt"


def test_defaults():
    house = House("hesse-darmstadt", "Hesse-Darmstadt")
    assert house.parent is None
    assert house.founder is None
    assert house.founded is None
    assert house.exiled is None


def test_full_fields_round_trip():
    house = House(
        "hesse-darmstadt",
        "Hesse-Darmstadt",
        parent="hesse",
        founder="hesse-darmstadt.ludwig-ix",
        founded=Event(1740),
        exiled=Event(1918),
    )
    assert house.parent == "hesse"
    assert house.founder == "hesse-darmstadt.ludwig-ix"
    assert house.founded == Event(1740)
    assert house.exiled == Event(1918)


def test_missing_required_fields_raises_validation_error():
    with pytest.raises(ValidationError):
        House()  # type: ignore[call-arg]
