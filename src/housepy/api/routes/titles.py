from fastapi import APIRouter, Query, Request

from housepy.api.jsonapi import resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, TitleDocument, title_to_resource
from housepy.data import titles
from housepy.models.types import Slug
from housepy.utils import find_by_slug

router = APIRouter()


@router.get("")
async def list_titles(
    request: Request, include: str | None = Query(default=None)
) -> TitleDocument:
    resources = [title_to_resource(t, request) for t in titles]
    return TitleDocument(
        data=resources,
        included=resolve_included(resources, include, request, RESOURCE_BUILDERS),
    )


@router.get("/{slug}", name="get_title")
async def get_title(
    slug: Slug, request: Request, include: str | None = Query(default=None)
) -> TitleDocument:
    resource = title_to_resource(find_by_slug(titles, slug), request)
    return TitleDocument(
        data=resource,
        included=resolve_included([resource], include, request, RESOURCE_BUILDERS),
    )
