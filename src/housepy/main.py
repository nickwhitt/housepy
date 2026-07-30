from fastapi import FastAPI

from housepy.api.routes import people, titles

app = FastAPI(title="HousePy")

app.include_router(people.router, prefix="/people", tags=["people"])
app.include_router(titles.router, prefix="/titles", tags=["titles"])


@app.get("/")
async def root():
    return {"message": "HousePy API"}
