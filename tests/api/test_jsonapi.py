from starlette.datastructures import URL

from housepy.api.jsonapi import (
    Relationship,
    ResourceIdentifier,
    ResourceLinks,
    paginate,
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
        def _build(id_, session, request):
            calls.append((type_, id_))
            return {"type": type_, "id": id_}

        return _build

    return {"people": build("people"), "titles": build("titles")}


def test_no_include_returns_none():
    resources = [_person_resource("p1", ["t1"])]
    assert resolve_included(resources, None, None, _fake_builders([]), None) is None
    assert resolve_included(resources, "", None, _fake_builders([]), None) is None


def test_single_type_resolves_matching_identifiers():
    resources = [_person_resource("p1", ["t1"])]
    calls = []
    result = resolve_included(resources, "titles", None, _fake_builders(calls), None)
    assert calls == [("titles", "t1")]
    assert result == [{"type": "titles", "id": "t1"}]


def test_duplicate_identifiers_deduped():
    resources = [
        _person_resource("p1", ["t1"]),
        _person_resource("p2", ["t1"]),
    ]
    calls = []
    resolve_included(resources, "titles", None, _fake_builders(calls), None)
    assert calls == [("titles", "t1")]


def test_unmatched_include_returns_none():
    resources = [_person_resource("p1", ["t1"])]
    result = resolve_included(resources, "nonexistent", None, _fake_builders([]), None)
    assert result is None


def test_resource_with_no_relationships_is_skipped():
    resource = PersonResource(
        id="p1", attributes=PersonAttributes(name=Name(), birth=Event(1900))
    )
    assert resource.relationships is None
    result = resolve_included([resource], "titles", None, _fake_builders([]), None)
    assert result is None


def test_mixed_single_and_multi_value_relationships_flatten():
    resources = [
        _person_resource("p1", ["t1"]),
        _title_resource("t2", ["p2", "p3"]),
    ]
    calls = []
    result = resolve_included(
        resources, "titles,people", None, _fake_builders(calls), None
    )
    assert set(calls) == {("titles", "t1"), ("people", "p2"), ("people", "p3")}
    assert result is not None
    assert len(result) == 3


def test_resource_links_self_alias_round_trips():
    links = ResourceLinks(self="http://testserver/people/p1")
    assert links.self_link == "http://testserver/people/p1"


def _fake_request(url="http://testserver/v1/people"):
    # paginate() only ever touches `request.url.include_query_params`, so a
    # bare object carrying a real starlette URL is enough — no need for a
    # full Request/ASGI scope.
    return type("FakeRequest", (), {"url": URL(url)})()


def test_paginate_slices_by_page_size():
    items = list(range(25))
    page_items, links = paginate(items, _fake_request(), 1, 10)
    assert page_items == items[:10]
    assert links.next is not None
    assert links.prev is None


def test_paginate_middle_page_has_prev_and_next():
    items = list(range(25))
    page_items, links = paginate(items, _fake_request(), 2, 10)
    assert page_items == items[10:20]
    assert links.prev is not None
    assert links.next is not None


def test_paginate_last_page_has_no_next():
    items = list(range(25))
    page_items, links = paginate(items, _fake_request(), 3, 10)
    assert page_items == items[20:25]
    assert links.next is None
    assert links.last == links.self_link


def test_paginate_clamps_page_size_to_max():
    items = list(range(250))
    page_items, _ = paginate(items, _fake_request(), 1, 1000)
    assert len(page_items) == 100  # MAX_PAGE_SIZE


def test_paginate_clamps_page_size_below_one():
    items = list(range(5))
    page_items, _ = paginate(items, _fake_request(), 1, 0)
    assert len(page_items) == 1


def test_paginate_clamps_page_number_below_one():
    items = list(range(5))
    page_items, links = paginate(items, _fake_request(), -3, 10)
    assert page_items == items
    assert links.prev is None


def test_paginate_empty_collection_has_no_prev_or_next():
    page_items, links = paginate([], _fake_request(), 1, 20)
    assert page_items == []
    assert links.prev is None
    assert links.next is None
    assert links.first == links.last == links.self_link
