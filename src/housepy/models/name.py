from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar, Literal, Self

type NameParts = Literal[
    "given", "family", "prefix", "chosen", "title", "group", "first"
]


@dataclass
class Name:
    """A set of names by which an individual is known."""

    given: str | None = None
    family: str | None = None
    prefix: str | None = None
    chosen: str | None = None
    title: str | None = None
    group: str | None = None
    format: Sequence[NameParts] = field(default_factory=lambda: Name.HOUSE)

    FULL: ClassVar[Sequence[NameParts]] = ["title", "given", "prefix", "family"]
    REGNAL: ClassVar[Sequence[NameParts]] = ["title", "first", "prefix", "group"]
    HOUSE: ClassVar[Sequence[NameParts]] = ["title", "first", "prefix", "family"]

    @property
    def first(self) -> str:
        """A familiar name; either the chosen or first given name."""
        return self.chosen or (self.given or "").split(" ")[0]

    def __str__(self) -> str:
        return " ".join(filter(None, [getattr(self, part) for part in self.format]))

    @classmethod
    def regnal(
        cls, chosen: str, family: str | None = None, given: str | None = None
    ) -> Self:
        return cls(chosen=chosen, family=family, given=given, format=cls.REGNAL)
