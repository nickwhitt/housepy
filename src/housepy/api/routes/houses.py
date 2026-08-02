from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from housepy.api.jsonapi import resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, HouseDocument, house_to_resource
from housepy.db import loader
from housepy.models.types import Slug

router = APIRouter()


@router.get("", name="list_houses")
async def list_houses(
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
) -> HouseDocument:
    resources = [
        house_to_resource(h, session, request) for h in loader.list_houses(session)
    ]
    return HouseDocument(
        data=resources,
        included=resolve_included(
            resources, include, request, RESOURCE_BUILDERS, session
        ),
    )


@router.get("/{slug}", name="get_house")
async def get_house(
    slug: Slug,
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
) -> HouseDocument:
    resource = house_to_resource(loader.fetch_house(session, slug), session, request)
    return HouseDocument(
        data=resource,
        included=resolve_included(
            [resource], include, request, RESOURCE_BUILDERS, session
        ),
    )
