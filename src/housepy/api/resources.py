from collections.abc import Callable
from dataclasses import asdict

from fastapi import Request

from housepy.api.jsonapi import (
    Relationship,
    Resource,
    ResourceIdentifier,
    ResourceLinks,
)
from housepy.data import people, titles
from housepy.utils import find_by_slug


def person_to_resource(
    person, request: Request, include_relationships: bool = True
) -> Resource:
    relationships = None
    if include_relationships:
        relationships = {
            "titles": Relationship(
                data=[
                    ResourceIdentifier(type="titles", id=t.title) for t in person.titles
                ]
            )
        }
    return Resource(
        type="people",
        id=person.slug,
        attributes={
            "name": asdict(person.name),
            "birth": asdict(person.birth),
            "death": asdict(person.death) if person.death else None,
            "tenures": [asdict(t) for t in person.titles],
        },
        relationships=relationships,
        links=ResourceLinks(self=str(request.url_for("get_person", slug=person.slug))),
    )


def title_to_resource(
    title, request: Request, include_relationships: bool = True
) -> Resource:
    relationships = None
    if include_relationships:
        holders = [p for p in people if any(t.title == title.slug for t in p.titles)]
        relationships = {
            "holders": Relationship(
                data=[ResourceIdentifier(type="people", id=p.slug) for p in holders]
            )
        }
    return Resource(
        type="titles",
        id=title.slug,
        attributes={"name": title.name, "group": title.group},
        relationships=relationships,
        links=ResourceLinks(self=str(request.url_for("get_title", slug=title.slug))),
    )


def _build_person(slug: str, request: Request) -> Resource:
    return person_to_resource(
        find_by_slug(people, slug), request, include_relationships=False
    )


def _build_title(slug: str, request: Request) -> Resource:
    return title_to_resource(
        find_by_slug(titles, slug), request, include_relationships=False
    )


RESOURCE_BUILDERS: dict[str, Callable[[str, Request], Resource]] = {
    "people": _build_person,
    "titles": _build_title,
}
