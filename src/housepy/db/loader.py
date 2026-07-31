import sqlite3
from dataclasses import dataclass
from importlib import resources

from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.house import House
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title
from housepy.models.types import Slug


@dataclass
class LoadedData:
    people: list[Person]
    titles: list[Title]
    families: list[Family]
    houses: list[House]


def get_connection() -> sqlite3.Connection:
    """Opens an in-memory SQLite connection loaded from the committed seed.

    Kept alive by the caller (see `data.py`) as a free baseline for future
    runtime querying — unused for now, since the app still serves reads from
    the materialized Python objects below, not live SQL.
    """

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    seed_sql = resources.files("housepy.db").joinpath("seed.sql").read_text()
    conn.executescript(seed_sql)
    return conn


def _event_or_none(events: dict[int, Event], event_id: int | None) -> Event | None:
    return events[event_id] if event_id is not None else None


def _load_events(conn: sqlite3.Connection) -> dict[int, Event]:
    events = {}
    for row in conn.execute("SELECT * FROM events"):
        name_fields = (
            row["name_given"],
            row["name_family"],
            row["name_prefix"],
            row["name_chosen"],
            row["name_title"],
            row["name_suffix"],
        )
        name = Name(*name_fields) if any(name_fields) else None
        events[row["id"]] = Event(
            row["year"], row["month"], row["day"], row["place"], name
        )
    return events


def _load_houses(conn: sqlite3.Connection, events: dict[int, Event]) -> list[House]:
    return [
        House(
            slug=row["slug"],
            name=row["name"],
            parent=row["parent_slug"],
            founder=row["founder_slug"],
            founded=_event_or_none(events, row["founded_event_id"]),
            exiled=_event_or_none(events, row["exiled_event_id"]),
        )
        for row in conn.execute("SELECT * FROM houses")
    ]


def _load_titles(conn: sqlite3.Connection) -> list[Title]:
    return [
        Title(slug=row["slug"], name=row["name"], group=row["group_name"])
        for row in conn.execute("SELECT * FROM titles")
    ]


def _load_tenures(
    conn: sqlite3.Connection, events: dict[int, Event], person_slug: Slug
) -> list[Tenure]:
    return [
        Tenure(
            title=row["title_slug"],
            start=events[row["start_event_id"]],
            end=_event_or_none(events, row["end_event_id"]),
            ceremony=_event_or_none(events, row["ceremony_event_id"]),
            pretense=bool(row["pretense"]),
            regent_for=row["regent_for_slug"],
        )
        # `ORDER BY id` preserves insertion order — which is not necessarily
        # chronological (a person's tenures can be authored/listed in any
        # order) and must match `seed.sql`'s INSERT order exactly.
        for row in conn.execute(
            "SELECT * FROM tenures WHERE person_slug = ? ORDER BY id", (person_slug,)
        )
    ]


def _load_people(conn: sqlite3.Connection, events: dict[int, Event]) -> list[Person]:
    people = []
    for row in conn.execute("SELECT * FROM people"):
        name = Name(
            row["name_given"],
            row["name_family"],
            row["name_prefix"],
            row["name_chosen"],
            row["name_title"],
            row["name_suffix"],
        )
        people.append(
            Person(
                slug=row["slug"],
                name=name,
                birth=events[row["birth_event_id"]],
                death=_event_or_none(events, row["death_event_id"]),
                titles=_load_tenures(conn, events, row["slug"]),
                house=row["house_slug"],
            )
        )
    return people


def _load_families(conn: sqlite3.Connection, events: dict[int, Event]) -> list[Family]:
    families = []
    for row in conn.execute("SELECT * FROM families"):
        children = [
            child_row["child_slug"]
            for child_row in conn.execute(
                "SELECT child_slug FROM family_children "
                "WHERE family_slug = ? ORDER BY position",
                (row["slug"],),
            )
        ]
        families.append(
            Family(
                slug=row["slug"],
                father=row["father_slug"],
                mother=row["mother_slug"],
                children=children,
                married=_event_or_none(events, row["married_event_id"]),
                divorced=_event_or_none(events, row["divorced_event_id"]),
            )
        )
    return families


def materialize(conn: sqlite3.Connection) -> LoadedData:
    events = _load_events(conn)
    return LoadedData(
        people=_load_people(conn, events),
        titles=_load_titles(conn),
        families=_load_families(conn, events),
        houses=_load_houses(conn, events),
    )
