from fastapi import Request
from pydantic import BaseModel

from housepy.api.jsonapi import Relationship, ResourceIdentifier, ResourceLinks
from housepy.data import people, titles
from housepy.models.event import Event
from housepy.models.name import Name
from housepy.models.title import Tenure
from housepy.utils import find_by_slug

# ---------- Person ----------


class PersonAttributes(BaseModel):
    name: Name
    birth: Event
    death: Event | None = None
    tenures: list[Tenure] = []


class PersonRelationships(BaseModel):
    titles: Relationship | None = None


class PersonResource(BaseModel):
    type: str = "people"
    id: str
    attributes: PersonAttributes
    relationships: PersonRelationships | None = None
    links: ResourceLinks | None = None


# ---------- Title ----------


class TitleAttributes(BaseModel):
    name: str
    group: str | None = None


class TitleRelationships(BaseModel):
    holders: Relationship | None = None


class TitleResource(BaseModel):
    type: str = "titles"
    id: str
    attributes: TitleAttributes
    relationships: TitleRelationships | None = None
    links: ResourceLinks | None = None


# ---------- included / documents ----------

IncludedResource = PersonResource | TitleResource


class PersonDocument(BaseModel):
    data: PersonResource | list[PersonResource]
    included: list[IncludedResource] | None = None


class TitleDocument(BaseModel):
    data: TitleResource | list[TitleResource]
    included: list[IncludedResource] | None = None


# ---------- builders ----------


def person_to_resource(
    person, request: Request, include_relationships: bool = True
) -> PersonResource:
    relationships = None
    if include_relationships:
        relationships = PersonRelationships(
            titles=Relationship(
                data=[
                    ResourceIdentifier(type="titles", id=t.title) for t in person.titles
                ]
            )
        )
    return PersonResource(
        id=person.slug,
        attributes=PersonAttributes(
            name=person.name,
            birth=person.birth,
            death=person.death,
            tenures=person.titles,
        ),
        relationships=relationships,
        links=ResourceLinks(self=str(request.url_for("get_person", slug=person.slug))),
    )


def title_to_resource(
    title, request: Request, include_relationships: bool = True
) -> TitleResource:
    relationships = None
    if include_relationships:
        holders = [p for p in people if any(t.title == title.slug for t in p.titles)]
        relationships = TitleRelationships(
            holders=Relationship(
                data=[ResourceIdentifier(type="people", id=p.slug) for p in holders]
            )
        )
    return TitleResource(
        id=title.slug,
        attributes=TitleAttributes(name=title.name, group=title.group),
        relationships=relationships,
        links=ResourceLinks(self=str(request.url_for("get_title", slug=title.slug))),
    )


def _build_person(slug: str, request: Request):
    return person_to_resource(
        find_by_slug(people, slug), request, include_relationships=False
    )


def _build_title(slug: str, request: Request):
    return title_to_resource(
        find_by_slug(titles, slug), request, include_relationships=False
    )


RESOURCE_BUILDERS = {"people": _build_person, "titles": _build_title}
