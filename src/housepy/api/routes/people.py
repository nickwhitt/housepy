from fastapi import APIRouter, Query, Request

from housepy.api.jsonapi import resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, PersonDocument, person_to_resource
from housepy.data import people
from housepy.models.types import Slug
from housepy.utils import find_by_slug

router = APIRouter()


@router.get("", name="list_people")
async def list_people(
    request: Request, include: str | None = Query(default=None)
) -> PersonDocument:
    resources = [person_to_resource(p, request) for p in people]
    return PersonDocument(
        data=resources,
        included=resolve_included(resources, include, request, RESOURCE_BUILDERS),
    )


@router.get("/{slug}", name="get_person")
async def get_person(
    slug: Slug, request: Request, include: str | None = Query(default=None)
) -> PersonDocument:
    resource = person_to_resource(find_by_slug(people, slug), request)
    return PersonDocument(
        data=resource,
        included=resolve_included([resource], include, request, RESOURCE_BUILDERS),
    )
