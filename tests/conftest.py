import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from housepy.db.loader import get_session, load_seed_data
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
from housepy.main import app

_slug_counter = itertools.count(1)


def _in_memory_engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    event.listens_for(engine, "connect")(
        lambda dbapi_conn, _: dbapi_conn.execute("PRAGMA foreign_keys=ON")
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def engine():
    """Seed.sql-backed engine — use for tests/db/, which validates the real
    authored dataset."""
    engine = _in_memory_engine()
    load_seed_data(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def api_session():
    """Fresh, empty schema per test — tests/api/ populates it via the make_*
    fixtures below instead of using the shared seed.sql dataset."""
    with Session(_in_memory_engine()) as session:
        yield session


@pytest.fixture
def client(api_session):
    # api_session owns the session lifecycle; shared with the make_* fixtures
    # so a route handler sees data a test just built, without a commit.
    def override_get_session():
        yield api_session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_event(api_session):
    def _make_event(*, slug=None, year=1900, month=0, day=0, place=None):
        slug = slug or f"test.event-{next(_slug_counter)}"
        event = EventTable(slug=slug, year=year, month=month, day=day, place=place)
        api_session.add(event)
        api_session.flush()
        return event

    return _make_event


@pytest.fixture
def make_house(api_session):
    def _make_house(
        *,
        slug=None,
        name="Test House",
        parent=None,
        founder=None,
        founded=None,
        exiled=None,
    ):
        slug = slug or f"test.house-{next(_slug_counter)}"
        house = HouseTable(
            slug=slug,
            name=name,
            parent_slug=parent.slug if parent else None,
            founder_slug=founder.slug if founder else None,
            founded_event_slug=founded.slug if founded else None,
            exiled_event_slug=exiled.slug if exiled else None,
        )
        api_session.add(house)
        api_session.flush()
        return house

    return _make_house


@pytest.fixture
def make_title(api_session):
    def _make_title(*, slug=None, name="Test Title", group=None):
        slug = slug or f"test.title-{next(_slug_counter)}"
        title = TitleTable(slug=slug, name=name, group_name=group)
        api_session.add(title)
        api_session.flush()
        return title

    return _make_title


@pytest.fixture
def make_person(api_session, make_event):
    def _make_person(
        *,
        slug=None,
        given="Test",
        family=None,
        prefix=None,
        chosen=None,
        birth=None,
        death=None,
        house=None,
        sex=None,
    ):
        slug = slug or f"test.person-{next(_slug_counter)}"
        birth = birth or make_event(year=1900)
        person = PersonTable(
            slug=slug,
            name_given=given,
            name_family=family,
            name_prefix=prefix,
            name_chosen=chosen,
            birth_event_slug=birth.slug,
            death_event_slug=death.slug if death else None,
            house_slug=house.slug if house else None,
            sex=sex,
        )
        api_session.add(person)
        api_session.flush()
        return person

    return _make_person


@pytest.fixture
def make_tenure(api_session, make_event):
    def _make_tenure(
        *,
        person,
        title,
        start=None,
        end=None,
        ceremony=None,
        pretense=False,
        regent_for=None,
    ):
        start = start or make_event(year=1950)
        tenure = TenureTable(
            person_slug=person.slug,
            title_slug=title.slug,
            start_event_slug=start.slug,
            end_event_slug=end.slug if end else None,
            ceremony_event_slug=ceremony.slug if ceremony else None,
            pretense=pretense,
            regent_for_slug=regent_for.slug if regent_for else None,
        )
        api_session.add(tenure)
        api_session.flush()
        return tenure

    return _make_tenure


@pytest.fixture
def make_family(api_session):
    def _make_family(
        *,
        slug=None,
        father=None,
        mother=None,
        children=None,
        married=None,
        divorced=None,
    ):
        slug = slug or f"test.family-{next(_slug_counter)}"
        family = FamilyTable(
            slug=slug,
            father_slug=father.slug if father else None,
            mother_slug=mother.slug if mother else None,
            married_event_slug=married.slug if married else None,
            divorced_event_slug=divorced.slug if divorced else None,
        )
        api_session.add(family)
        api_session.flush()
        for position, child in enumerate(children or []):
            api_session.add(
                FamilyChildTable(
                    family_slug=slug, child_slug=child.slug, position=position
                )
            )
        api_session.flush()
        return family

    return _make_family
