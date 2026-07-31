from fastapi import APIRouter, Query, Request

from housepy.api.jsonapi import resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, HouseDocument, house_to_resource
from housepy.data import houses
from housepy.models.types import Slug
from housepy.utils import find_by_slug

router = APIRouter()


@router.get("", name="list_houses")
async def list_houses(
    request: Request, include: str | None = Query(default=None)
) -> HouseDocument:
    resources = [house_to_resource(h, request) for h in houses]
    return HouseDocument(
        data=resources,
        included=resolve_included(resources, include, request, RESOURCE_BUILDERS),
    )


@router.get("/{slug}", name="get_house")
async def get_house(
    slug: Slug, request: Request, include: str | None = Query(default=None)
) -> HouseDocument:
    resource = house_to_resource(find_by_slug(houses, slug), request)
    return HouseDocument(
        data=resource,
        included=resolve_included([resource], include, request, RESOURCE_BUILDERS),
    )
