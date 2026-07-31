from pydantic.dataclasses import dataclass

from housepy.models.event import Event
from housepy.models.types import Slug


@dataclass
class House:
    """A noble house/dynasty.

    Slug convention: a bare identifier (e.g. `windsor`,
    `saxe-coburg-and-gotha`) — the root of the `house.identifier` convention
    used by `Person`/`Title` slugs, so it needs no compound form of its own.
    `parent` references the house this one is a cadet branch of, if any.
    """

    slug: Slug
    name: str
    parent: Slug | None = None
    founder: Slug | None = None
    founded: Event | None = None
    exiled: Event | None = None

    def __str__(self) -> str:
        return self.name
