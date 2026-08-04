from http import HTTPStatus
from urllib.parse import urljoin

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from housepy import __version__
from housepy.api.jsonapi import (
    DiscoveryDocument,
    DiscoveryMeta,
    ErrorDocument,
    ErrorObject,
)
from housepy.api.routes import families, houses, people, titles

JSONAPI_MEDIA_TYPE = "application/vnd.api+json"


class JSONAPIResponse(JSONResponse):
    media_type = JSONAPI_MEDIA_TYPE


app = FastAPI(
    title="HousePy", version=__version__, default_response_class=JSONAPIResponse
)

app.include_router(people.router, prefix="/v1/people", tags=["people"])
app.include_router(titles.router, prefix="/v1/titles", tags=["titles"])
app.include_router(families.router, prefix="/v1/families", tags=["families"])
app.include_router(houses.router, prefix="/v1/houses", tags=["houses"])


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONAPIResponse:
    document = ErrorDocument(
        errors=[
            ErrorObject(
                status=str(exc.status_code),
                title=HTTPStatus(exc.status_code).phrase,
                detail=str(exc.detail),
            )
        ]
    )
    return JSONAPIResponse(status_code=exc.status_code, content=document.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONAPIResponse:
    document = ErrorDocument(
        errors=[
            ErrorObject(
                status=str(HTTPStatus.UNPROCESSABLE_ENTITY),
                title=HTTPStatus.UNPROCESSABLE_ENTITY.phrase,
                detail="{}: {}".format(
                    ".".join(str(part) for part in error["loc"]), error["msg"]
                ),
            )
            for error in exc.errors()
        ]
    )
    return JSONAPIResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content=document.model_dump()
    )


@app.get("/")
async def root(request: Request) -> DiscoveryDocument:
    base = str(request.base_url)
    return DiscoveryDocument(
        meta=DiscoveryMeta(
            name="HousePy API",
            documentation={
                "swagger": urljoin(base, request.app.docs_url),
                "redoc": urljoin(base, request.app.redoc_url),
                "openapi": urljoin(base, request.app.openapi_url),
            },
        ),
        links={
            "people": str(request.url_for("list_people")),
            "titles": str(request.url_for("list_titles")),
            "families": str(request.url_for("list_families")),
            "houses": str(request.url_for("list_houses")),
        },
    )
