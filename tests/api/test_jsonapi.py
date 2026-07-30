from housepy.api.jsonapi import (
    Relationship,
    ResourceIdentifier,
    ResourceLinks,
    resolve_included,
)
from housepy.api.resources import (
    PersonAttributes,
    PersonRelationships,
    PersonResource,
    TitleAttributes,
    TitleRelationships,
    TitleResource,
)
from housepy.models.event import Event
from housepy.models.name import Name


def _person_resource(slug, title_slugs):
    return PersonResource(
        id=slug,
        attributes=PersonAttributes(name=Name(), birth=Event(1900)),
        relationships=PersonRelationships(
            titles=Relationship(
                data=[ResourceIdentifier(type="titles", id=t) for t in title_slugs]
            )
        ),
    )


def _title_resource(slug, holder_slugs):
    return TitleResource(
        id=slug,
        attributes=TitleAttributes(name=slug),
        relationships=TitleRelationships(
            holders=Relationship(
                data=[ResourceIdentifier(type="people", id=p) for p in holder_slugs]
            )
        ),
    )


def _fake_builders(calls):
    def build(type_):
        def _build(id_, request):
            calls.append((type_, id_))
            return {"type": type_, "id": id_}

        return _build

    return {"people": build("people"), "titles": build("titles")}


def test_no_include_returns_none():
    resources = [_person_resource("p1", ["t1"])]
    assert resolve_included(resources, None, None, _fake_builders([])) is None
    assert resolve_included(resources, "", None, _fake_builders([])) is None


def test_single_type_resolves_matching_identifiers():
    resources = [_person_resource("p1", ["t1"])]
    calls = []
    result = resolve_included(resources, "titles", None, _fake_builders(calls))
    assert calls == [("titles", "t1")]
    assert result == [{"type": "titles", "id": "t1"}]


def test_duplicate_identifiers_deduped():
    resources = [
        _person_resource("p1", ["t1"]),
        _person_resource("p2", ["t1"]),
    ]
    calls = []
    resolve_included(resources, "titles", None, _fake_builders(calls))
    assert calls == [("titles", "t1")]


def test_unmatched_include_returns_none():
    resources = [_person_resource("p1", ["t1"])]
    result = resolve_included(resources, "nonexistent", None, _fake_builders([]))
    assert result is None


def test_resource_with_no_relationships_is_skipped():
    resource = PersonResource(
        id="p1", attributes=PersonAttributes(name=Name(), birth=Event(1900))
    )
    assert resource.relationships is None
    result = resolve_included([resource], "titles", None, _fake_builders([]))
    assert result is None


def test_mixed_single_and_multi_value_relationships_flatten():
    resources = [
        _person_resource("p1", ["t1"]),
        _title_resource("t2", ["p2", "p3"]),
    ]
    calls = []
    result = resolve_included(resources, "titles,people", None, _fake_builders(calls))
    assert set(calls) == {("titles", "t1"), ("people", "p2"), ("people", "p3")}
    assert result is not None
    assert len(result) == 3


def test_resource_links_self_alias_round_trips():
    links = ResourceLinks(self="http://testserver/people/p1")
    assert links.self_link == "http://testserver/people/p1"
