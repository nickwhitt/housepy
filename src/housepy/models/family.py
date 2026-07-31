from collections.abc import Sequence
from dataclasses import dataclass, field

from housepy.models.event import Event
from housepy.models.types import Slug


@dataclass
class Family:
    """An atomic family consisting of two parents and a set of children.

    Slug convention: `{father}+{mother}+family-N`, omitting whichever
    parent is unknown (e.g. `{father}+family-1` if the mother is unknown).
    If both parents are unknown, anchor on a known child instead, or fall
    back to a bare `family-N`. `N` disambiguates multiple families sharing
    the same known parent(s). Not enforced — a documented convention, not a
    validated rule (this was previously an auto-computed property using the
    literal string "unknown" for an absent parent, but that collided
    whenever two different families shared the same known/unknown
    combination — switched to an explicit authored field instead, same as
    `Person`/`Title`).
    """

    slug: Slug
    father: Slug | None = None
    mother: Slug | None = None
    children: Sequence[Slug] = field(default_factory=list)
    married: Event | None = None
    divorced: Event | None = None
