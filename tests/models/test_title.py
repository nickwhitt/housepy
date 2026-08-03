from housepy.models.event import Event
from housepy.models.title import Tenure, Title


def test_title_str():
    assert str(Title("hesse-darmstadt.landgrave", "Landgrave of Hesse-Darmstadt")) == (
        "Landgrave of Hesse-Darmstadt"
    )


def test_tenure_defaults():
    tenure = Tenure(title="hesse-darmstadt.landgrave", start=Event(1768, 10, 12))
    assert tenure.end is None
    assert tenure.ceremony is None
    assert tenure.pretense is False
    assert tenure.regent_for is None
