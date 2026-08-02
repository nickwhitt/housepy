from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from housepy.api.jsonapi import resolve_included
from housepy.api.resources import RESOURCE_BUILDERS, TitleDocument, title_to_resource
from housepy.db import loader
from housepy.models.types import Slug

router = APIRouter()


@router.get("", name="list_titles")
async def list_titles(
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
) -> TitleDocument:
    resources = [
        title_to_resource(t, session, request) for t in loader.list_titles(session)
    ]
    return TitleDocument(
        data=resources,
        included=resolve_included(
            resources, include, request, RESOURCE_BUILDERS, session
        ),
    )


@router.get("/{slug}", name="get_title")
async def get_title(
    slug: Slug,
    request: Request,
    session: Session = Depends(loader.get_session),
    include: str | None = Query(default=None),
) -> TitleDocument:
    resource = title_to_resource(loader.fetch_title(session, slug), session, request)
    return TitleDocument(
        data=resource,
        included=resolve_included(
            [resource], include, request, RESOURCE_BUILDERS, session
        ),
    )
