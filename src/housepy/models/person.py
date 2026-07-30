import datetime
from dataclasses import dataclass, field

from housepy.models.event import Event
from housepy.models.name import Name
from housepy.models.title import Tenure


@dataclass
class Person:
    """An individual, living or deceased."""

    slug: str
    name: Name
    birth: Event
    death: Event | None = None
    titles: list[Tenure] = field(default_factory=list)

    def __str__(self) -> str:
        return str(self.name)

    @property
    def age(self) -> int:
        """Calculates age based on known birth and death events.

        Properly calculates age before/after birthdate of death year when both dates
        are known, otherwise assumes death occured after birthdate. If no death event
        is recorded, today's date will be treated as date of death.
        """

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
