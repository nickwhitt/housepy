from collections.abc import Callable
from typing import Literal

from fastapi import Request
from pydantic import BaseModel

from housepy.api.jsonapi import Relationship, ResourceIdentifier, ResourceLinks
from housepy.data import families, people, titles
from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title
from housepy.models.types import Slug
from housepy.utils import find_by_slug

type ResourceType = Literal["people", "titles", "families"]

# ---------- Person ----------


class PersonAttributes(BaseModel):
    name: Name
    birth: Event
    death: Event | None = None
    tenures: list[Tenure] = []


class PersonRelationships(BaseModel):
    titles: Relationship | None = None


class PersonResource(BaseModel):
    type: ResourceType = "people"
    id: Slug
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
    type: ResourceType = "titles"
    id: Slug
    attributes: TitleAttributes
    relationships: TitleRelationships | None = None
    links: ResourceLinks | None = None


# ---------- Family ----------


class FamilyAttributes(BaseModel):
    married: Event | None = None
    divorced: Event | None = None


class FamilyRelationships(BaseModel):
    father: Relationship | None = None
    mother: Relationship | None = None
    children: Relationship | None = None


class FamilyResource(BaseModel):
    type: ResourceType = "families"
    id: Slug
    attributes: FamilyAttributes
    relationships: FamilyRelationships | None = None
    links: ResourceLinks | None = None


# ---------- included / documents ----------

IncludedResource = PersonResource | TitleResource | FamilyResource


class PersonDocument(BaseModel):
    data: PersonResource | list[PersonResource]
    included: list[IncludedResource] | None = None


class TitleDocument(BaseModel):
    data: TitleResource | list[TitleResource]
    included: list[IncludedResource] | None = None


class FamilyDocument(BaseModel):
    data: FamilyResource | list[FamilyResource]
    included: list[IncludedResource] | None = None


# ---------- builders ----------


def person_to_resource(
    person: Person, request: Request, include_relationships: bool = True
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
    title: Title, request: Request, include_relationships: bool = True
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


def family_to_resource(
    family: Family, request: Request, include_relationships: bool = True
) -> FamilyResource:
    relationships = None
    if include_relationships:
        relationships = FamilyRelationships(
            father=Relationship(
                data=ResourceIdentifier(type="people", id=family.father)
                if family.father
                else None
            ),
            mother=Relationship(
                data=ResourceIdentifier(type="people", id=family.mother)
                if family.mother
                else None
            ),
            children=Relationship(
                data=[ResourceIdentifier(type="people", id=c) for c in family.children]
            ),
        )
    return FamilyResource(
        id=family.slug,
        attributes=FamilyAttributes(married=family.married, divorced=family.divorced),
        relationships=relationships,
        links=ResourceLinks(self=str(request.url_for("get_family", slug=family.slug))),
    )


def _build_person(slug: Slug, request: Request):
    return person_to_resource(
        find_by_slug(people, slug), request, include_relationships=False
    )


def _build_title(slug: Slug, request: Request):
    return title_to_resource(
        find_by_slug(titles, slug), request, include_relationships=False
    )


def _build_family(slug: Slug, request: Request):
    return family_to_resource(
        find_by_slug(families, slug), request, include_relationships=False
    )


RESOURCE_BUILDERS: dict[ResourceType, Callable[[Slug, Request], IncludedResource]] = {
    "people": _build_person,
    "titles": _build_title,
    "families": _build_family,
}
