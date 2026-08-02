from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field


class ResourceIdentifier(BaseModel):
    type: str
    id: str


class Relationship(BaseModel):
    data: ResourceIdentifier | list[ResourceIdentifier] | None = None


class ResourceLinks(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    self_link: str | None = Field(default=None, alias="self")


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


def resolve_included(resources, include, request, resource_builders, session):
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
