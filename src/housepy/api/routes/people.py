from fastapi import APIRouter, Query, Request

from housepy.api.jsonapi import Document, resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, person_to_resource
from housepy.data import people
from housepy.utils import find_by_slug

router = APIRouter()


@router.get("")
async def list_people(
    request: Request, include: str | None = Query(default=None)
) -> Document:
    resources = [person_to_resource(p, request) for p in people]
    return Document(
        data=resources,
        included=resolve_included(resources, include, request, RESOURCE_BUILDERS),
    )


@router.get("/{slug}", name="get_person")
async def get_person(
    slug: str, request: Request, include: str | None = Query(default=None)
) -> Document:
    resource = person_to_resource(find_by_slug(people, slug), request)
    return Document(
        data=resource,
        included=resolve_included([resource], include, request, RESOURCE_BUILDERS),
    )
