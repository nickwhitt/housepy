from fastapi import HTTPException, status


def find_by_slug(collection: list, slug: str):
    try:
        return next(item for item in collection if item.slug == slug)
    except StopIteration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
