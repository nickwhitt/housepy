from collections.abc import Callable
from typing import Literal

from fastapi import Request
from pydantic import BaseModel

from housepy.api.jsonapi import Relationship, ResourceIdentifier, ResourceLinks
from housepy.data import families, houses, people, titles
from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.house import House
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title
from housepy.models.types import Slug
from housepy.utils import find_by_slug

type ResourceType = Literal["people", "titles", "families", "houses"]

# ---------- Person ----------


class PersonAttributes(BaseModel):
    name: Name
    birth: Event
    death: Event | None = None
    tenures: list[Tenure] = []


class PersonRelationships(BaseModel):
    titles: Relationship | None = None
    families: Relationship | None = None
    house: Relationship | None = None


class PersonResource(BaseModel):
    type: ResourceType = "people"
    id: Slug
    attributes: PersonAttributes
    relationships: PersonRelationships | None = None
    links: ResourceLinks | None = None


# ---------- Title ----------


class TitleHolding(BaseModel):
    person: Slug
    start: Event
    end: Event | None = None
    ceremony: Event | None = None
    pretense: bool = False
    regent_for: Slug | None = None


class TitleAttributes(BaseModel):
    name: str
    group: str | None = None
    tenures: list[TitleHolding] = []


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


# ---------- House ----------


class HouseAttributes(BaseModel):
    name: str
    founded: Event | None = None
    exiled: Event | None = None


class HouseRelationships(BaseModel):
    parent: Relationship | None = None
    cadet_branches: Relationship | None = None
    founder: Relationship | None = None
    members: Relationship | None = None


class HouseResource(BaseModel):
    type: ResourceType = "houses"
    id: Slug
    attributes: HouseAttributes
    relationships: HouseRelationships | None = None
    links: ResourceLinks | None = None


# ---------- included / documents ----------

IncludedResource = PersonResource | TitleResource | FamilyResource | HouseResource


class PersonDocument(BaseModel):
    data: PersonResource | list[PersonResource]
    included: list[IncludedResource] | None = None


class TitleDocument(BaseModel):
    data: TitleResource | list[TitleResource]
    included: list[IncludedResource] | None = None


class FamilyDocument(BaseModel):
    data: FamilyResource | list[FamilyResource]
    included: list[IncludedResource] | None = None


class HouseDocument(BaseModel):
    data: HouseResource | list[HouseResource]
    included: list[IncludedResource] | None = None


# ---------- builders ----------


def person_to_resource(
    person: Person, request: Request, include_relationships: bool = True
) -> PersonResource:
    relationships = None
    if include_relationships:
        member_of = [
            f for f in families if person.slug in (f.father, f.mother, *f.children)
        ]
        relationships = PersonRelationships(
            titles=Relationship(
                data=[
                    ResourceIdentifier(type="titles", id=t.title) for t in person.titles
                ]
            ),
            families=Relationship(
                data=[ResourceIdentifier(type="families", id=f.slug) for f in member_of]
            ),
            house=Relationship(
                data=ResourceIdentifier(type="houses", id=person.house)
                if person.house
                else None
            ),
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
    tenures = [
        TitleHolding(
            person=p.slug,
            start=t.start,
            end=t.end,
            ceremony=t.ceremony,
            pretense=t.pretense,
            regent_for=t.regent_for,
        )
        for p in people
        for t in p.titles
        if t.title == title.slug
    ]
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
        attributes=TitleAttributes(name=title.name, group=title.group, tenures=tenures),
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


def house_to_resource(
    house: House, request: Request, include_relationships: bool = True
) -> HouseResource:
    relationships = None
    if include_relationships:
        cadet_branches = [h for h in houses if h.parent == house.slug]
        members = [p for p in people if p.house == house.slug]
        relationships = HouseRelationships(
            parent=Relationship(
                data=ResourceIdentifier(type="houses", id=house.parent)
                if house.parent
                else None
            ),
            cadet_branches=Relationship(
                data=[
                    ResourceIdentifier(type="houses", id=h.slug) for h in cadet_branches
                ]
            ),
            founder=Relationship(
                data=ResourceIdentifier(type="people", id=house.founder)
                if house.founder
                else None
            ),
            members=Relationship(
                data=[ResourceIdentifier(type="people", id=p.slug) for p in members]
            ),
        )
    return HouseResource(
        id=house.slug,
        attributes=HouseAttributes(
            name=house.name, founded=house.founded, exiled=house.exiled
        ),
        relationships=relationships,
        links=ResourceLinks(self=str(request.url_for("get_house", slug=house.slug))),
    )


# These four builders back RESOURCE_BUILDERS, used only to build "bare"
# `included` entries (include_relationships=False, so `relationships` comes
# back `null` rather than omitted — an intentional signal that this
# resource has no relationships to report here, not a missing field).
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


def _build_house(slug: Slug, request: Request):
    return house_to_resource(
        find_by_slug(houses, slug), request, include_relationships=False
    )


RESOURCE_BUILDERS: dict[ResourceType, Callable[[Slug, Request], IncludedResource]] = {
    "people": _build_person,
    "titles": _build_title,
    "families": _build_family,
    "houses": _build_house,
}
