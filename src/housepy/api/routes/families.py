from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from housepy.api.jsonapi import resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, FamilyDocument, family_to_resource
from housepy.db import loader
from housepy.models.types import Slug

router = APIRouter()


@router.get("", name="list_families")
async def list_families(
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
) -> FamilyDocument:
    resources = [family_to_resource(f, request) for f in loader.list_families(session)]
    return FamilyDocument(
        data=resources,
        included=resolve_included(
            resources, include, request, RESOURCE_BUILDERS, session
        ),
    )


@router.get("/{slug}", name="get_family")
async def get_family(
    slug: Slug,
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
) -> FamilyDocument:
    resource = family_to_resource(loader.fetch_family(session, slug), request)
    return FamilyDocument(
        data=resource,
        included=resolve_included(
            [resource], include, request, RESOURCE_BUILDERS, session
        ),
    )
