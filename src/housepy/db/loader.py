"""Query functions mapping the SQLAlchemy schema (`db/tables.py`) onto the domain
dataclasses in `models/`. Each function takes a `Session` and runs an explicit
query; `get_session()` is the FastAPI dependency that supplies it.

`_events_by_id`, `_tenures_by_person`, and `_family_children_by_family` each load
their whole table once and index by id/slug in Python, rather than querying
per-item — avoids N+1 queries in the `list_*`/relationship functions that build
more than one `Person`/`Family`.
"""

from collections.abc import Generator
from importlib import resources
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy import Engine, create_engine, event, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from housepy.db.tables import (
    Base,
    EventTable,
    FamilyChildTable,
    FamilyTable,
    HouseTable,
    PersonTable,
    TenureTable,
    TitleTable,
)
from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.house import House
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title
from housepy.models.types import Sex, Slug

_engine: Engine | None = None


def _get_engine() -> Engine:
    """Lazily creates the shared in-memory engine on first use, not at import
    time. Tests substitute their own data via `app.dependency_overrides` on
    `get_session` instead of using this engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        event.listens_for(_engine, "connect")(
            lambda dbapi_conn, _: dbapi_conn.execute("PRAGMA foreign_keys=ON")
        )
        Base.metadata.create_all(_engine)
        load_seed_data(_engine)
    return _engine


def load_seed_data(engine: Engine) -> None:
    # executescript() runs seed.sql's multiple statements in one call;
    # exec_driver_sql only supports a single statement.
    seed_sql = resources.files("housepy.db").joinpath("seed.sql").read_text()
    raw_conn = engine.raw_connection()
    try:
        raw_conn.executescript(seed_sql)
        raw_conn.commit()
    finally:
        raw_conn.close()


def get_session() -> Generator[Session]:
    with Session(_get_engine()) as session:
        yield session


# ---------- events (surrogate id, identity-less in the domain — see tables.py) ----


def _event_or_none(events: dict[int, Event], event_id: int | None) -> Event | None:
    return events[event_id] if event_id is not None else None


def _event_from_row(row: EventTable) -> Event:
    name_fields = (
        row.name_given,
        row.name_family,
        row.name_prefix,
        row.name_chosen,
        row.name_title,
        row.name_suffix,
    )
    name = Name(*name_fields) if any(name_fields) else None
    return Event(row.year, row.month, row.day, row.place, name)


def _events_by_id(session: Session) -> dict[int, Event]:
    rows = session.execute(select(EventTable)).scalars()
    return {row.id: _event_from_row(row) for row in rows}


# ---------- tenures ----------


def _tenure_from_row(row: TenureTable, events: dict[int, Event]) -> Tenure:
    return Tenure(
        title=row.title_slug,
        start=events[row.start_event_id],
        end=_event_or_none(events, row.end_event_id),
        ceremony=_event_or_none(events, row.ceremony_event_id),
        pretense=row.pretense,
        regent_for=row.regent_for_slug,
    )


def _tenures_by_person(
    session: Session, events: dict[int, Event]
) -> dict[Slug, list[Tenure]]:
    # ORDER BY id preserves insertion order, which is not necessarily
    # chronological — do not sort by date.
    rows = session.execute(select(TenureTable).order_by(TenureTable.id)).scalars()
    tenures_by_person: dict[Slug, list[Tenure]] = {}
    for row in rows:
        tenures_by_person.setdefault(row.person_slug, []).append(
            _tenure_from_row(row, events)
        )
    return tenures_by_person


# ---------- people ----------


def _name_from_person_row(row: PersonTable) -> Name:
    return Name(
        row.name_given,
        row.name_family,
        row.name_prefix,
        row.name_chosen,
        row.name_title,
        row.name_suffix,
    )


def _person_from_row(
    row: PersonTable,
    tenures_by_person: dict[Slug, list[Tenure]],
    events: dict[int, Event],
) -> Person:
    return Person(
        slug=row.slug,
        name=_name_from_person_row(row),
        birth=events[row.birth_event_id],
        death=_event_or_none(events, row.death_event_id),
        titles=tenures_by_person.get(row.slug, []),
        house=row.house_slug,
        # DB column is a plain str, narrowed via the ck_people_sex CheckConstraint.
        sex=cast(Sex | None, row.sex),
    )


def fetch_person(session: Session, slug: Slug) -> Person:
    row = session.get(PersonTable, slug)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    events = _events_by_id(session)
    return _person_from_row(row, _tenures_by_person(session, events), events)


def list_people(session: Session) -> list[Person]:
    events = _events_by_id(session)
    tenures_by_person = _tenures_by_person(session, events)
    rows = session.execute(select(PersonTable)).scalars()
    return [_person_from_row(row, tenures_by_person, events) for row in rows]


# ---------- titles ----------


def _title_from_row(row: TitleTable) -> Title:
    return Title(slug=row.slug, name=row.name, group=row.group_name)


def fetch_title(session: Session, slug: Slug) -> Title:
    row = session.get(TitleTable, slug)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return _title_from_row(row)


def list_titles(session: Session) -> list[Title]:
    rows = session.execute(select(TitleTable)).scalars()
    return [_title_from_row(row) for row in rows]


# ---------- houses ----------


def _house_from_row(row: HouseTable, events: dict[int, Event]) -> House:
    return House(
        slug=row.slug,
        name=row.name,
        parent=row.parent_slug,
        founder=row.founder_slug,
        founded=_event_or_none(events, row.founded_event_id),
        exiled=_event_or_none(events, row.exiled_event_id),
    )


def fetch_house(session: Session, slug: Slug) -> House:
    row = session.get(HouseTable, slug)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return _house_from_row(row, _events_by_id(session))


def list_houses(session: Session) -> list[House]:
    events = _events_by_id(session)
    rows = session.execute(select(HouseTable)).scalars()
    return [_house_from_row(row, events) for row in rows]


# ---------- families ----------


def _family_children_by_family(session: Session) -> dict[Slug, list[Slug]]:
    rows = session.execute(
        select(FamilyChildTable).order_by(FamilyChildTable.position)
    ).scalars()
    children_by_family: dict[Slug, list[Slug]] = {}
    for row in rows:
        children_by_family.setdefault(row.family_slug, []).append(row.child_slug)
    return children_by_family


def _family_from_row(
    row: FamilyTable,
    children_by_family: dict[Slug, list[Slug]],
    events: dict[int, Event],
) -> Family:
    return Family(
        slug=row.slug,
        father=row.father_slug,
        mother=row.mother_slug,
        children=children_by_family.get(row.slug, []),
        married=_event_or_none(events, row.married_event_id),
        divorced=_event_or_none(events, row.divorced_event_id),
    )


def fetch_family(session: Session, slug: Slug) -> Family:
    row = session.get(FamilyTable, slug)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return _family_from_row(
        row, _family_children_by_family(session), _events_by_id(session)
    )


def list_families(session: Session) -> list[Family]:
    events = _events_by_id(session)
    children_by_family = _family_children_by_family(session)
    rows = session.execute(select(FamilyTable)).scalars()
    return [_family_from_row(row, children_by_family, events) for row in rows]


# ---------- relationship-support queries (used by api/resources.py) ----------


def families_for_person(session: Session, slug: Slug) -> list[Family]:
    events = _events_by_id(session)
    children_by_family = _family_children_by_family(session)
    rows = session.execute(
        select(FamilyTable)
        .outerjoin(FamilyChildTable, FamilyChildTable.family_slug == FamilyTable.slug)
        .where(
            or_(
                FamilyTable.father_slug == slug,
                FamilyTable.mother_slug == slug,
                FamilyChildTable.child_slug == slug,
            )
        )
        .distinct()
    ).scalars()
    return [_family_from_row(row, children_by_family, events) for row in rows]


def tenures_for_title(session: Session, slug: Slug) -> list[tuple[Slug, Tenure]]:
    events = _events_by_id(session)
    rows = session.execute(
        select(TenureTable)
        .where(TenureTable.title_slug == slug)
        .order_by(TenureTable.id)
    ).scalars()
    return [(row.person_slug, _tenure_from_row(row, events)) for row in rows]


def holders_for_title(session: Session, slug: Slug) -> list[Person]:
    events = _events_by_id(session)
    tenures_by_person = _tenures_by_person(session, events)
    rows = session.execute(
        select(PersonTable)
        .join(TenureTable, TenureTable.person_slug == PersonTable.slug)
        .where(TenureTable.title_slug == slug)
        .distinct()
    ).scalars()
    return [_person_from_row(row, tenures_by_person, events) for row in rows]


def cadet_branches(session: Session, slug: Slug) -> list[House]:
    events = _events_by_id(session)
    rows = session.execute(
        select(HouseTable).where(HouseTable.parent_slug == slug)
    ).scalars()
    return [_house_from_row(row, events) for row in rows]


def members_of_house(session: Session, slug: Slug) -> list[Person]:
    events = _events_by_id(session)
    tenures_by_person = _tenures_by_person(session, events)
    rows = session.execute(
        select(PersonTable).where(PersonTable.house_slug == slug)
    ).scalars()
    return [_person_from_row(row, tenures_by_person, events) for row in rows]
