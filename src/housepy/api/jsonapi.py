from collections.abc import Callable
from typing import Any

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field


class ResourceIdentifier(BaseModel):
    type: str
    id: str


class Relationship(BaseModel):
    data: ResourceIdentifier | list[ResourceIdentifier] | None = None


class ResourceLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    self_link: str | None = Field(default=None, alias="self")


class Resource(BaseModel):
    type: str
    id: str
    attributes: dict[str, Any]
    relationships: dict[str, Relationship] | None = None
    links: ResourceLinks | None = None


class Document(BaseModel):
    data: Resource | list[Resource]
    included: list[Resource] | None = None


def resolve_included(
    resources: list[Resource],
    include: str | None,
    request: Request,
    resource_builders: dict[str, Callable[[str, Request], Resource]],
) -> list[Resource] | None:
    """Resolve one level of relationship identifiers into bare resources
    for the `included` array. Only relationship types present in both
    `include` and `resource_builders` are resolved; no dot-path/nested
    includes are supported (deferred — see housepy notes)."""
    if not include:
        return None

    wanted_types = set(include.split(","))
    identifiers = {
        (identifier.type, identifier.id)
        for resource in resources
        for rel in (resource.relationships or {}).values()
        for identifier in (
            rel.data if isinstance(rel.data, list) else [rel.data] if rel.data else []
        )
        if identifier.type in wanted_types
    }

    built = [
        resource_builders[type_](id_, request)
        for type_, id_ in identifiers
        if type_ in resource_builders
    ]
    return built or None
