from dataclasses import dataclass
from datetime import date
from functools import cached_property, total_ordering

from housepy.models.name import Name


@total_ordering
@dataclass
class Event:
    """Represents something which happened on a specific date; i.e. birth, death."""

    year: int
    month: int = 0
    day: int = 0
    place: str | None = None
    name: Name | None = None

    @cached_property
    def date(self) -> date | None:
        return (
            date(self.year, self.month, self.day) if self.month and self.day else None
        )

    def __str__(self) -> str:
        return ", ".join(
            filter(
                None,
                [
                    f"as {self.name}" if self.name else None,
                    self.date.strftime("%-d %b %Y") if self.date else str(self.year),
                    self.place,
                ],
            )
        )

    def __lt__(self, other):
        return self.date < other.date
