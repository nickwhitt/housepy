from pathlib import Path

from sqlalchemy import create_engine, event

from housepy.db.loader import load_seed_data
from housepy.db.tables import Base

SEED_PATH = Path("src/housepy/db/seed.sql")
DB_PATH = Path("housepy.db")


def main() -> None:
    DB_PATH.unlink(missing_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    event.listens_for(engine, "connect")(
        lambda dbapi_conn, _: dbapi_conn.execute("PRAGMA foreign_keys=ON")
    )
    Base.metadata.create_all(engine)
    load_seed_data(engine)
    print(
        f"Built {DB_PATH} from {SEED_PATH} — open it in DB Browser for SQLite to edit."
    )


if __name__ == "__main__":
    main()
