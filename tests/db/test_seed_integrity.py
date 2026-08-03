from sqlalchemy import Engine, create_engine, event, text

from housepy.db.loader import load_seed_data
from housepy.db.tables import Base


def _build_engine() -> Engine:
    engine = create_engine("sqlite://")
    event.listens_for(engine, "connect")(
        lambda dbapi_conn, _: dbapi_conn.execute("PRAGMA foreign_keys=ON")
    )
    Base.metadata.create_all(engine)
    load_seed_data(engine)
    return engine


def test_seed_loads_without_integrity_errors():
    engine = _build_engine()
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_key_check")).fetchall() == []


def test_seed_row_counts():
    # Lower bounds, not exact matches — the fixture dataset only grows via
    # data-entry PRs, so a `>=` here never needs bumping for a legitimate
    # addition. It still catches a table silently loading empty.
    minimums = {
        "events": 12,
        "houses": 2,
        "titles": 2,
        "people": 3,
        "tenures": 3,
        "families": 1,
        "family_children": 1,
    }
    engine = _build_engine()
    with engine.connect() as conn:
        counts = {
            table: conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            for table in minimums
        }
    for table, minimum in minimums.items():
        assert counts[table] >= minimum, (
            f"{table} has {counts[table]} rows, expected at least {minimum}"
        )
