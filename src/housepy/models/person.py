import datetime
from dataclasses import field

from pydantic.dataclasses import dataclass

from housepy.models.event import Event
from housepy.models.name import Name
from housepy.models.title import Tenure
from housepy.models.types import Sex, Slug


@dataclass
class Person:
    """An individual, living or deceased.

    Slug convention: `house.identifier` (e.g. `hesse-darmstadt.ludwig-i`).
    """

    slug: Slug
    name: Name
    birth: Event
    death: Event | None = None
    titles: list[Tenure] = field(default_factory=list)
    house: Slug | None = None
    sex: Sex | None = None

    def __str__(self) -> str:
        return str(self.name)

    @property
    def age(self) -> int:
        """Age at death, or as of today if still living. Falls back to a
        year-only calculation if the death date has no month/day."""

        if self.death and not self.death.date:
            return self.death.year - self.birth.year

        death = (
            self.death.date
            if self.death and self.death.date
            else datetime.datetime.now(tz=datetime.UTC).date()
        )

        _age = death.year - self.birth.year
        if (death.month, death.day) < (self.birth.month, self.birth.day):
            _age -= 1

        return _age
