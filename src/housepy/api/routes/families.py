from fastapi import APIRouter, Query, Request

from housepy.api.jsonapi import resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, FamilyDocument, family_to_resource
from housepy.data import families
from housepy.models.types import Slug
from housepy.utils import find_by_slug

router = APIRouter()


@router.get("")
async def list_families(
    request: Request, include: str | None = Query(default=None)
) -> FamilyDocument:
    resources = [family_to_resource(f, request) for f in families]
    return FamilyDocument(
        data=resources,
        included=resolve_included(resources, include, request, RESOURCE_BUILDERS),
    )


@router.get("/{slug}", name="get_family")
async def get_family(
    slug: Slug, request: Request, include: str | None = Query(default=None)
) -> FamilyDocument:
    resource = family_to_resource(find_by_slug(families, slug), request)
    return FamilyDocument(
        data=resource,
        included=resolve_included([resource], include, request, RESOURCE_BUILDERS),
    )
