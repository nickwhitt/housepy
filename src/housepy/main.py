from fastapi import FastAPI

from housepy.api.routes import families, people, titles

app = FastAPI(title="HousePy")

app.include_router(people.router, prefix="/people", tags=["people"])
app.include_router(titles.router, prefix="/titles", tags=["titles"])
app.include_router(families.router, prefix="/families", tags=["families"])


@app.get("/")
async def root():
    return {"message": "HousePy API"}
