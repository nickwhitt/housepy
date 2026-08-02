from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from housepy.api.jsonapi import DEFAULT_PAGE_SIZE, paginate, resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, PersonDocument, person_to_resource
from housepy.db import loader
from housepy.models.types import Slug

router = APIRouter()


@router.get("", name="list_people")
async def list_people(
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
    page_number: int = Query(default=1, alias="page[number]"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, alias="page[size]"),
) -> PersonDocument:
    page_items, links = paginate(
        loader.list_people(session), request, page_number, page_size
    )
    resources = [person_to_resource(p, session, request) for p in page_items]
    return PersonDocument(
        data=resources,
        included=resolve_included(
            resources, include, request, RESOURCE_BUILDERS, session
        ),
        links=links,
    )


@router.get("/{slug}", name="get_person")
async def get_person(
    slug: Slug,
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
) -> PersonDocument:
    resource = person_to_resource(loader.fetch_person(session, slug), session, request)
    return PersonDocument(
        data=resource,
        included=resolve_included(
            [resource], include, request, RESOURCE_BUILDERS, session
        ),
    )
