from urllib.parse import urljoin

from fastapi import FastAPI, Request

from housepy.api.routes import families, houses, people, titles

app = FastAPI(title="HousePy")

app.include_router(people.router, prefix="/people", tags=["people"])
app.include_router(titles.router, prefix="/titles", tags=["titles"])
app.include_router(families.router, prefix="/families", tags=["families"])
app.include_router(houses.router, prefix="/houses", tags=["houses"])


@app.get("/")
async def root(request: Request) -> dict:
    base = str(request.base_url)
    return {
        "meta": {
            "name": "HousePy API",
            "documentation": {
                "swagger": urljoin(base, request.app.docs_url),
                "redoc": urljoin(base, request.app.redoc_url),
                "openapi": urljoin(base, request.app.openapi_url),
            },
        },
        "links": {
            "people": str(request.url_for("list_people")),
            "titles": str(request.url_for("list_titles")),
            "families": str(request.url_for("list_families")),
            "houses": str(request.url_for("list_houses")),
        },
    }
