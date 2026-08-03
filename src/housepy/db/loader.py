"""Query functions mapping the SQLAlchemy schema (`db/tables.py`) onto the domain
dataclasses in `models/`. Every function here takes a `Session` and runs an explicit,
targeted query — there is no ORM object graph (`tables.py` deliberately has no
`relationship()`) and no bulk "load everything" step; each function queries exactly
what it needs, and `get_session()` is the FastAPI dependency that supplies the session
routes use to call them.
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
    """Lazily creates the shared in-memory engine on first use — not at import time,
    so merely importing this module (or `housepy.main`) touches no database. This is
    what gives tests (via `app.dependency_overrides` on `get_session`) a real seam to
    substitute different data instead of this production engine ever running.
    """
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
    # seed.sql has multiple statements in one script (BEGIN/INSERT.../COMMIT) —
    # exec_driver_sql only runs a single statement, so this goes through the
    # DBAPI connection's executescript() directly, same as raw sqlite3 would.
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


def _tenures_for_person(
    session: Session, events: dict[int, Event], slug: Slug
) -> list[Tenure]:
    # ORDER BY id preserves insertion order — not necessarily chronological (a
    # person's tenures can be authored/listed in any order) — sorting by date
    # would silently change behavior.
    rows = session.execute(
        select(TenureTable)
        .where(TenureTable.person_slug == slug)
        .order_by(TenureTable.id)
    ).scalars()
    return [_tenure_from_row(row, events) for row in rows]


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
    row: PersonTable, session: Session, events: dict[int, Event]
) -> Person:
    return Person(
        slug=row.slug,
        name=_name_from_person_row(row),
        birth=events[row.birth_event_id],
        death=_event_or_none(events, row.death_event_id),
        titles=_tenures_for_person(session, events, row.slug),
        house=row.house_slug,
        # PersonTable.sex is a plain `str | None` column — tables.py deliberately
        # doesn't mirror domain-level types (see its module docstring), so the
        # narrowing to Sex is only visible via the DB's own `ck_people_sex`
        # CheckConstraint, not to the type checker.
        sex=cast(Sex | None, row.sex),
    )


def fetch_person(session: Session, slug: Slug) -> Person:
    row = session.get(PersonTable, slug)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return _person_from_row(row, session, _events_by_id(session))


def list_people(session: Session) -> list[Person]:
    events = _events_by_id(session)
    rows = session.execute(select(PersonTable)).scalars()
    return [_person_from_row(row, session, events) for row in rows]


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


def _family_children(session: Session, slug: Slug) -> list[Slug]:
    rows = session.execute(
        select(FamilyChildTable)
        .where(FamilyChildTable.family_slug == slug)
        .order_by(FamilyChildTable.position)
    ).scalars()
    return [row.child_slug for row in rows]


def _family_from_row(
    row: FamilyTable, session: Session, events: dict[int, Event]
) -> Family:
    return Family(
        slug=row.slug,
        father=row.father_slug,
        mother=row.mother_slug,
        children=_family_children(session, row.slug),
        married=_event_or_none(events, row.married_event_id),
        divorced=_event_or_none(events, row.divorced_event_id),
    )


def fetch_family(session: Session, slug: Slug) -> Family:
    row = session.get(FamilyTable, slug)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return _family_from_row(row, session, _events_by_id(session))


def list_families(session: Session) -> list[Family]:
    events = _events_by_id(session)
    rows = session.execute(select(FamilyTable)).scalars()
    return [_family_from_row(row, session, events) for row in rows]


# ---------- relationship-support queries (used by api/resources.py) ----------


def families_for_person(session: Session, slug: Slug) -> list[Family]:
    events = _events_by_id(session)
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
    return [_family_from_row(row, session, events) for row in rows]


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
    rows = session.execute(
        select(PersonTable)
        .join(TenureTable, TenureTable.person_slug == PersonTable.slug)
        .where(TenureTable.title_slug == slug)
        .distinct()
    ).scalars()
    return [_person_from_row(row, session, events) for row in rows]


def cadet_branches(session: Session, slug: Slug) -> list[House]:
    events = _events_by_id(session)
    rows = session.execute(
        select(HouseTable).where(HouseTable.parent_slug == slug)
    ).scalars()
    return [_house_from_row(row, events) for row in rows]


def members_of_house(session: Session, slug: Slug) -> list[Person]:
    events = _events_by_id(session)
    rows = session.execute(
        select(PersonTable).where(PersonTable.house_slug == slug)
    ).scalars()
    return [_person_from_row(row, session, events) for row in rows]
