from collections.abc import Callable, Iterable, Mapping
from typing import Protocol

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20


class ResourceIdentifier(BaseModel):
    type: str
    id: str


class Relationship(BaseModel):
    data: ResourceIdentifier | list[ResourceIdentifier] | None = None


class ResourceLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    self_link: str | None = Field(default=None, alias="self")


class DocumentLinks(BaseModel):
    """Top-level pagination links for a list response — `first`/`prev`/`next`/`last`
    are omitted (not null) when they don't apply, e.g. no `prev` on page 1."""

    model_config = ConfigDict(populate_by_name=True)
    self_link: str | None = Field(default=None, alias="self")
    first: str | None = None
    prev: str | None = None
    next: str | None = None
    last: str | None = None


class ErrorObject(BaseModel):
    status: str
    title: str
    detail: str | None = None


class ErrorDocument(BaseModel):
    errors: list[ErrorObject]


class DiscoveryMeta(BaseModel):
    name: str
    documentation: dict[str, str]


class DiscoveryDocument(BaseModel):
    """The `GET /` self-discovery document — see main.py's `root()`."""

    meta: DiscoveryMeta
    links: dict[str, str]


def paginate[T](
    items: list[T], request: Request, page_number: int, page_size: int
) -> tuple[list[T], DocumentLinks]:
    """Clamps `page[number]`/`page[size]` into valid range, slices `items`,
    and builds the matching top-level pagination links."""
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    page_number = max(1, page_number)
    total = len(items)
    last_page = max(1, -(-total // page_size))  # ceil division

    start = (page_number - 1) * page_size
    page_items = items[start : start + page_size]

    def url_for_page(page: int) -> str:
        return str(
            request.url.include_query_params(
                **{
                    "page[number]": page,
                    "page[size]": page_size,
                }
            )
        )

    links = DocumentLinks(
        self=url_for_page(page_number),
        first=url_for_page(1),
        prev=url_for_page(page_number - 1) if page_number > 1 else None,
        next=url_for_page(page_number + 1) if page_number < last_page else None,
        last=url_for_page(last_page),
    )
    return page_items, links


def _relationship_items(relationships: BaseModel | None) -> Iterable[Relationship]:
    """Yield the Relationship values on any *Relationships model, regardless
    of its concrete type (PersonRelationships, TitleRelationships, ...)."""
    if relationships is None:
        return []
    return [
        value
        for name in type(relationships).model_fields
        if (value := getattr(relationships, name)) is not None
    ]


class _HasRelationships(Protocol):
    """Structural stand-in for PersonResource/TitleResource/FamilyResource/
    HouseResource, so this module doesn't import from resources.py."""

    @property
    def relationships(self) -> BaseModel | None: ...


def resolve_included[T](
    resources: Iterable[_HasRelationships],
    include: str | None,
    request: Request,
    resource_builders: Mapping[str, Callable[[str, Session, Request], T]],
    session: Session,
) -> list[T] | None:
    """Resolve one level of relationship identifiers into bare resources for
    the `included` array. Works against any resource objects that expose a
    `.relationships` attribute — no dependency on which resource types exist."""
    if not include:
        return None

    wanted_types = set(include.split(","))
    identifiers = {
        (identifier.type, identifier.id)
        for resource in resources
        for rel in _relationship_items(resource.relationships)
        for identifier in (
            rel.data if isinstance(rel.data, list) else [rel.data] if rel.data else []
        )
        if identifier.type in wanted_types
    }

    built = [
        resource_builders[type_](id_, session, request)
        for type_, id_ in identifiers
        if type_ in resource_builders
    ]
    return built or None
