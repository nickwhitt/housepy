from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from housepy.api.jsonapi import DEFAULT_PAGE_SIZE, paginate, resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, HouseDocument, house_to_resource
from housepy.db import loader
from housepy.models.types import Slug

router = APIRouter()


@router.get("", name="list_houses")
async def list_houses(
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
    page_number: int = Query(default=1, alias="page[number]"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, alias="page[size]"),
) -> HouseDocument:
    page_items, links = paginate(
        loader.list_houses(session), request, page_number, page_size
    )
    resources = [house_to_resource(h, session, request) for h in page_items]
    return HouseDocument(
        data=resources,
        included=resolve_included(
            resources, include, request, RESOURCE_BUILDERS, session
        ),
        links=links,
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
