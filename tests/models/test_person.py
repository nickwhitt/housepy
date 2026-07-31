import pytest
from freezegun import freeze_time
from pydantic import ValidationError

from housepy.models.event import Event
from housepy.models.name import Name
from housepy.models.person import Person


def _person(birth, death=None):
    return Person("test.person", Name(given="Test"), birth, death)


def test_age_full_dates_before_birthday_in_death_year():
    person = _person(Event(1719, 12, 15), Event(1790, 4, 6))
    assert person.age == 70


def test_age_full_dates_after_birthday_in_death_year():
    person = _person(Event(1719, 3, 1), Event(1790, 4, 6))
    assert person.age == 71


def test_age_year_only_death():
    person = _person(Event(1719, 12, 15), Event(1790))
    assert person.age == 71


@freeze_time("2026-07-30")
def test_age_living_person():
    person = _person(Event(2000, 1, 1))
    assert person.age == 26


def test_str_delegates_to_name():
    person = _person(Event(1719, 12, 15))
    assert str(person) == str(person.name)


def test_missing_required_fields_raises_validation_error():
    with pytest.raises(ValidationError):
        Person()  # type: ignore[call-arg]
