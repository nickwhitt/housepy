from pydantic.dataclasses import dataclass


@dataclass
class Name:
    """A set of names by which an individual is known.

    `prefix` is the nobiliary particle attached to `family` for display
    (e.g. "of", "d'", "von") — kept as a separate field so search/sort can
    match on `family` alone without accounting for the particle. `suffix`
    is a trailing epithet (e.g. "the Great", "the Bald").
    """

    given: str | None = None
    family: str | None = None
    prefix: str | None = None
    chosen: str | None = None
    title: str | None = None
    suffix: str | None = None

    @property
    def first(self) -> str:
        """A familiar name; either the chosen or first given name."""
        return self.chosen or (self.given or "").split(" ")[0]

    def __str__(self) -> str:
        parts = [self.title, self.first, self.prefix, self.family, self.suffix]
        return " ".join(filter(None, parts))
