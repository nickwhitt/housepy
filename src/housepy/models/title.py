from pydantic.dataclasses import dataclass

from housepy.models.event import Event
from housepy.models.types import Slug


@dataclass
class Title:
    """A stable, shared title entity (e.g. "Landgrave of Hesse-Darmstadt").

    Slug convention: `realm.office` (e.g. `hesse-darmstadt.landgrave`,
    `england.king`) — territorial/institutional, independent of whichever
    house/dynasty currently holds the title.
    """

    slug: Slug
    name: str
    group: str | None = None

    def __str__(self) -> str:
        return self.name


@dataclass
class Tenure:
    title: Slug
    start: Event
    end: Event | None = None
    ceremony: Event | None = None
    pretense: bool = False
    regent_for: Slug | None = None  # the monarch being acted for
