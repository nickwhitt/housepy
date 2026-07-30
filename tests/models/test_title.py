import pytest

from housepy.models.event import Event
from housepy.models.title import Tenure, Title


def test_title_str():
    assert str(Title("hesse-darmstadt.landgrave", "Landgrave of Hesse-Darmstadt")) == (
        "Landgrave of Hesse-Darmstadt"
    )


def test_tenure_regnal_maps_events():
    accession = Event(1768, 10, 12)
    coronation = Event(1769, 1, 1)
    demise = Event(1790, 4, 6)
    tenure = Tenure.regnal(
        "hesse-darmstadt.landgrave", accession, coronation, demise, regent_for="x"
    )
    assert tenure.start == accession
    assert tenure.ceremony == coronation
    assert tenure.end == demise
    assert tenure.regent_for == "x"


def test_tenure_regnal_defaults_no_regent():
    tenure = Tenure.regnal("hesse-darmstadt.landgrave", Event(1768, 10, 12))
    assert tenure.regent_for is None


def test_tenure_peerage_maps_events():
    creation = Event(1806, 8, 14)
    investiture = Event(1806, 9, 1)
    extinction = Event(1830, 4, 6)
    tenure = Tenure.peerage(
        "hesse-and-by-rhine.grand-duke", creation, investiture, extinction
    )
    assert tenure.start == creation
    assert tenure.ceremony == investiture
    assert tenure.end == extinction


def test_tenure_peerage_rejects_regent_for():
    with pytest.raises(TypeError):
        Tenure.peerage(
            "hesse-and-by-rhine.grand-duke",
            Event(1806, 8, 14),
            regent_for="x",  # pyright: ignore[reportCallIssue]
        )
