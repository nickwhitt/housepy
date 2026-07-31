import sqlite3
from importlib import resources


def _load_seed() -> sqlite3.Connection:
    seed_sql = resources.files("housepy.db").joinpath("seed.sql").read_text()
    conn = sqlite3.connect(":memory:")
    conn.executescript(seed_sql)
    return conn


def test_seed_loads_without_integrity_errors():
    conn = _load_seed()
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_seed_row_counts():
    conn = _load_seed()
    counts = {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in [
            "events",
            "houses",
            "titles",
            "people",
            "tenures",
            "families",
            "family_children",
        ]
    }
    assert counts == {
        "events": 12,
        "houses": 2,
        "titles": 2,
        "people": 3,
        "tenures": 3,
        "families": 1,
        "family_children": 1,
    }
