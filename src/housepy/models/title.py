from dataclasses import dataclass
from typing import Self

from housepy.models.event import Event


@dataclass
class Title:
    slug: str
    name: str
    group: str | None = None

    def __str__(self) -> str:
        return self.name


@dataclass
class Tenure:
    title: str  # Title.slug
    start: Event
    end: Event | None = None
    ceremony: Event | None = None
    pretense: bool = False
    regent_for: str | None = None  # Person.slug of the monarch being acted for

    @classmethod
    def regnal(
        cls,
        title: str,
        accession: Event,
        coronation: Event | None = None,
        demise: Event | None = None,
        pretense: bool = False,
        regent_for: str | None = None,
    ) -> Self:
        return cls(
            title=title,
            start=accession,
            ceremony=coronation,
            end=demise,
            pretense=pretense,
            regent_for=regent_for,
        )

    @classmethod
    def peerage(
        cls,
        title: str,
        creation: Event,
        investiture: Event | None = None,
        extinction: Event | None = None,
        pretense: bool = False,
    ) -> Self:
        return cls(
            title=title,
            start=creation,
            ceremony=investiture,
            end=extinction,
            pretense=pretense,
        )
