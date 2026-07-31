from fastapi import HTTPException, status

from housepy.models.types import Slug


def find_by_slug(collection: list, slug: Slug):
    try:
        return next(item for item in collection if item.slug == slug)
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not found"
        ) from None
