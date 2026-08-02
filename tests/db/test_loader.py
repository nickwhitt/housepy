from housepy.db import loader
from housepy.models.event import Event
from housepy.models.name import Name


def test_list_includes_known_records(session):
    people = loader.list_people(session)
    assert {p.slug for p in people} >= {
        "hesse-darmstadt.ludwig-ix",
        "hesse-darmstadt.friederike-luise",
        "hesse-darmstadt.ludwig-i",
    }
    titles = loader.list_titles(session)
    assert {t.slug for t in titles} >= {
        "hesse-darmstadt.landgrave",
        "hesse-and-by-rhine.grand-duke",
    }
    houses = loader.list_houses(session)
    assert {h.slug for h in houses} >= {"hesse", "hesse-darmstadt"}
    families = loader.list_families(session)
    assert "hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1" in {
        f.slug for f in families
    }


def test_person_fields_round_trip(session):
    ludwig_ix = loader.fetch_person(session, "hesse-darmstadt.ludwig-ix")
    assert ludwig_ix.name == Name(chosen="Ludwig IX", given="Ludwig")
    assert ludwig_ix.birth == Event(
        1719, 12, 15, "Darmstadt, Landgraviate of Hesse-Darmstadt"
    )
    assert ludwig_ix.death == Event(1790, 4, 6)
    assert ludwig_ix.house == "hesse-darmstadt"


def test_tenure_order_is_preserved_not_chronological(session):
    ludwig_i = loader.fetch_person(session, "hesse-darmstadt.ludwig-i")
    # Grand-duke (starts 1806) is listed before landgrave (starts 1790) —
    # matches seed.sql's non-chronological insertion order.
    assert [t.title for t in ludwig_i.titles] == [
        "hesse-and-by-rhine.grand-duke",
        "hesse-darmstadt.landgrave",
    ]
    landgrave_tenure = ludwig_i.titles[1]
    assert landgrave_tenure.start.name == Name(chosen="Ludwig X")
    assert landgrave_tenure.end == Event(1806, 8, 14)


def test_event_without_name_materializes_to_none_not_empty_name(session):
    ludwig_ix = loader.fetch_person(session, "hesse-darmstadt.ludwig-ix")
    assert ludwig_ix.birth.name is None
    assert (
        str(ludwig_ix.birth)
        == "15 Dec 1719, Darmstadt, Landgraviate of Hesse-Darmstadt"
    )


def test_family_children_order_preserved(session):
    families = loader.list_families(session)
    assert families[0].children == ["hesse-darmstadt.ludwig-i"]
    assert families[0].father == "hesse-darmstadt.ludwig-ix"
    assert families[0].mother == "hesse-darmstadt.friederike-luise"


def test_house_founder_and_founded_event(session):
    hesse_darmstadt = loader.fetch_house(session, "hesse-darmstadt")
    assert hesse_darmstadt.founder == "hesse-darmstadt.ludwig-ix"
    assert hesse_darmstadt.founded == Event(1740)


def test_families_for_person(session):
    families = loader.families_for_person(session, "hesse-darmstadt.ludwig-ix")
    assert [f.slug for f in families] == [
        "hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1"
    ]


def test_holders_for_title(session):
    holders = loader.holders_for_title(session, "hesse-darmstadt.landgrave")
    assert {p.slug for p in holders} == {
        "hesse-darmstadt.ludwig-ix",
        "hesse-darmstadt.ludwig-i",
    }


def test_cadet_branches_and_members_of_house(session):
    assert [h.slug for h in loader.cadet_branches(session, "hesse")] == [
        "hesse-darmstadt"
    ]
    assert {p.slug for p in loader.members_of_house(session, "hesse-darmstadt")} == {
        "hesse-darmstadt.ludwig-ix",
        "hesse-darmstadt.friederike-luise",
        "hesse-darmstadt.ludwig-i",
    }
