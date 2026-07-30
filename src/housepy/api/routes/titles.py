from fastapi import APIRouter, Query, Request

from housepy.api.jsonapi import Document, resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, title_to_resource
from housepy.data import titles
from housepy.utils import find_by_slug

router = APIRouter()


@router.get("")
async def list_titles(
    request: Request, include: str | None = Query(default=None)
) -> Document:
    resources = [title_to_resource(t, request) for t in titles]
    return Document(
        data=resources,
        included=resolve_included(resources, include, request, RESOURCE_BUILDERS),
    )


@router.get("/{slug}", name="get_title")
async def get_title(
    slug: str, request: Request, include: str | None = Query(default=None)
) -> Document:
    resource = title_to_resource(find_by_slug(titles, slug), request)
    return Document(
        data=resource,
        included=resolve_included([resource], include, request, RESOURCE_BUILDERS),
    )
