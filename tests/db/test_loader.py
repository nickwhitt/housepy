from housepy.db.loader import get_connection, materialize
from housepy.models.event import Event
from housepy.models.name import Name


def _materialize():
    return materialize(get_connection())


def test_materializes_expected_counts():
    loaded = _materialize()
    assert len(loaded.people) == 3
    assert len(loaded.titles) == 2
    assert len(loaded.houses) == 2
    assert len(loaded.families) == 1


def test_person_fields_round_trip():
    loaded = _materialize()
    ludwig_ix = next(p for p in loaded.people if p.slug == "hesse-darmstadt.ludwig-ix")
    assert ludwig_ix.name == Name(chosen="Ludwig IX", given="Ludwig")
    assert ludwig_ix.birth == Event(
        1719, 12, 15, "Darmstadt, Landgraviate of Hesse-Darmstadt"
    )
    assert ludwig_ix.death == Event(1790, 4, 6)
    assert ludwig_ix.house == "hesse-darmstadt"


def test_tenure_order_is_preserved_not_chronological():
    loaded = _materialize()
    ludwig_i = next(p for p in loaded.people if p.slug == "hesse-darmstadt.ludwig-i")
    # Grand-duke (starts 1806) is listed before landgrave (starts 1790) —
    # matches data.py's original non-chronological list order.
    assert [t.title for t in ludwig_i.titles] == [
        "hesse-and-by-rhine.grand-duke",
        "hesse-darmstadt.landgrave",
    ]
    landgrave_tenure = ludwig_i.titles[1]
    assert landgrave_tenure.start.name == Name(chosen="Ludwig X")
    assert landgrave_tenure.end == Event(1806, 8, 14)


def test_event_without_name_materializes_to_none_not_empty_name():
    loaded = _materialize()
    ludwig_ix = next(p for p in loaded.people if p.slug == "hesse-darmstadt.ludwig-ix")
    assert ludwig_ix.birth.name is None
    assert (
        str(ludwig_ix.birth)
        == "15 Dec 1719, Darmstadt, Landgraviate of Hesse-Darmstadt"
    )


def test_family_children_order_preserved():
    loaded = _materialize()
    family = loaded.families[0]
    assert family.children == ["hesse-darmstadt.ludwig-i"]
    assert family.father == "hesse-darmstadt.ludwig-ix"
    assert family.mother == "hesse-darmstadt.friederike-luise"


def test_house_founder_and_founded_event():
    loaded = _materialize()
    hesse_darmstadt = next(h for h in loaded.houses if h.slug == "hesse-darmstadt")
    assert hesse_darmstadt.founder == "hesse-darmstadt.ludwig-ix"
    assert hesse_darmstadt.founded == Event(1740)
