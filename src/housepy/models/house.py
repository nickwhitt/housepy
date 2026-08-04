from pydantic.dataclasses import dataclass

from housepy.models.event import Event
from housepy.models.types import Slug


@dataclass
class House:
    """A noble house/dynasty.

    Slug convention: a bare identifier (e.g. `windsor`,
    `saxe-coburg-and-gotha`). `parent` references the house this one is a
    cadet branch of (a real lineage split — different people, e.g.
    Hesse-Darmstadt from Hesse). `renamed_from` references the house this
    one *is*, under an earlier name (the same people/institution, e.g.
    Windsor from Saxe-Coburg and Gotha in 1917) — mutually exclusive with
    `parent`, not a second flavor of it.
    """

    slug: Slug
    name: str
    parent: Slug | None = None
    renamed_from: Slug | None = None
    founder: Slug | None = None
    founded: Event | None = None

    def __str__(self) -> str:
        return self.name
