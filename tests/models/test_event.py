import pytest

from housepy.models.event import Event
from housepy.models.name import Name


def test_full_date_events_compare():
    earlier = Event(1790, 4, 6)
    later = Event(1806, 8, 14)
    assert earlier < later
    assert later > earlier
    assert earlier == Event(1790, 4, 6)


def test_year_only_events_are_not_orderable():
    with pytest.raises(TypeError):
        _ = Event(1790) < Event(1806)


def test_date_requires_month_and_day():
    assert Event(1790).date is None
    assert Event(1790, 4).date is None
    assert Event(1790, 4, 6).date is not None


def test_str_full_date():
    assert str(Event(1790, 4, 6)) == "6 Apr 1790"


def test_str_year_only():
    assert str(Event(1790)) == "1790"


def test_str_with_place():
    assert str(Event(1790, 4, 6, "Darmstadt")) == "6 Apr 1790, Darmstadt"


def test_str_with_name():
    event = Event(1790, 4, 6, name=Name.regnal("Ludwig X"))
    assert str(event) == "as Ludwig X, 6 Apr 1790"
