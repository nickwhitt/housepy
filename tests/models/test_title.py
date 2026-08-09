from housepy.models.event import Event
from housepy.models.title import Tenure, Title


def test_title_str():
    assert str(Title("hesse-darmstadt.landgrave", "Landgrave of Hesse-Darmstadt")) == (
        "Landgrave of Hesse-Darmstadt"
    )


def test_title_defaults():
    title = Title("hesse-darmstadt.landgrave", "Landgrave of Hesse-Darmstadt")
    assert title.group is None
    assert title.created is None
    assert title.abolished is None


def test_title_created_and_abolished_round_trip():
    title = Title(
        "hesse-darmstadt.landgrave",
        "Landgrave of Hesse-Darmstadt",
        created=Event(1567),
        abolished=Event(1806, 8, 14),
    )
    assert title.created == Event(1567)
    assert title.abolished == Event(1806, 8, 14)


def test_tenure_defaults():
    tenure = Tenure(title="hesse-darmstadt.landgrave", start=Event(1768, 10, 12))
    assert tenure.end is None
    assert tenure.ceremony is None
    assert tenure.pretense is False
    assert tenure.regent_for is None
