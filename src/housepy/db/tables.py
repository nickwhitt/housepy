"""SQLAlchemy schema for the seed-data store. Mirrors the domain model in
`models/` but isn't identical (a surrogate `tenures.id`, hand-authored
`events.slug`, flattened `Name` columns) — see README's "Editing the
dataset" section. No `relationship()` is defined; `loader.py` queries
explicitly via `select()`.
"""

from sqlalchemy import CheckConstraint, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventTable(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("month BETWEEN 0 AND 12", name="ck_events_month"),
        CheckConstraint("day BETWEEN 0 AND 31", name="ck_events_day"),
    )

    slug: Mapped[str] = mapped_column(primary_key=True)
    year: Mapped[int]
    month: Mapped[int] = mapped_column(default=0)
    day: Mapped[int] = mapped_column(default=0)
    place: Mapped[str | None]
    name_given: Mapped[str | None]
    name_family: Mapped[str | None]
    name_prefix: Mapped[str | None]
    name_chosen: Mapped[str | None]
    name_title: Mapped[str | None]
    name_suffix: Mapped[str | None]


class HouseTable(Base):
    __tablename__ = "houses"

    slug: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_slug: Mapped[str | None] = mapped_column(
        ForeignKey("houses.slug", deferrable=True, initially="DEFERRED")
    )
    renamed_from_slug: Mapped[str | None] = mapped_column(
        ForeignKey("houses.slug", deferrable=True, initially="DEFERRED")
    )
    founder_slug: Mapped[str | None] = mapped_column(
        ForeignKey("people.slug", deferrable=True, initially="DEFERRED")
    )
    founded_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )


class TitleTable(Base):
    __tablename__ = "titles"

    slug: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    group_name: Mapped[str | None]
    created_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )
    abolished_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )


class PersonTable(Base):
    __tablename__ = "people"
    __table_args__ = (
        CheckConstraint("sex IN ('male', 'female')", name="ck_people_sex"),
    )

    slug: Mapped[str] = mapped_column(primary_key=True)
    name_given: Mapped[str | None]
    name_family: Mapped[str | None]
    name_prefix: Mapped[str | None]
    name_chosen: Mapped[str | None]
    name_title: Mapped[str | None]
    name_suffix: Mapped[str | None]
    birth_event_slug: Mapped[str] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )
    death_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )
    house_slug: Mapped[str | None] = mapped_column(
        ForeignKey("houses.slug", deferrable=True, initially="DEFERRED")
    )
    birth_house_slug: Mapped[str | None] = mapped_column(
        ForeignKey("houses.slug", deferrable=True, initially="DEFERRED")
    )
    sex: Mapped[str | None] = mapped_column(default=None)


class TenureTable(Base):
    __tablename__ = "tenures"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_slug: Mapped[str] = mapped_column(
        ForeignKey("people.slug", deferrable=True, initially="DEFERRED")
    )
    title_slug: Mapped[str] = mapped_column(
        ForeignKey("titles.slug", deferrable=True, initially="DEFERRED")
    )
    start_event_slug: Mapped[str] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )
    end_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )
    ceremony_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )
    pretense: Mapped[bool] = mapped_column(default=False)
    regent_for_slug: Mapped[str | None] = mapped_column(
        ForeignKey("people.slug", deferrable=True, initially="DEFERRED")
    )


class FamilyTable(Base):
    __tablename__ = "families"

    slug: Mapped[str] = mapped_column(primary_key=True)
    father_slug: Mapped[str | None] = mapped_column(
        ForeignKey("people.slug", deferrable=True, initially="DEFERRED")
    )
    mother_slug: Mapped[str | None] = mapped_column(
        ForeignKey("people.slug", deferrable=True, initially="DEFERRED")
    )
    married_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )
    divorced_event_slug: Mapped[str | None] = mapped_column(
        ForeignKey("events.slug", deferrable=True, initially="DEFERRED")
    )


class FamilyChildTable(Base):
    __tablename__ = "family_children"
    __table_args__ = (PrimaryKeyConstraint("family_slug", "child_slug"),)

    family_slug: Mapped[str] = mapped_column(
        ForeignKey("families.slug", deferrable=True, initially="DEFERRED")
    )
    child_slug: Mapped[str] = mapped_column(
        ForeignKey("people.slug", deferrable=True, initially="DEFERRED")
    )
    position: Mapped[int]
