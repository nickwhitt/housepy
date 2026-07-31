import sqlite3
from pathlib import Path

SEED_PATH = Path("src/housepy/db/seed.sql")
DB_PATH = Path("housepy.db")


def main() -> None:
    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SEED_PATH.read_text())
    conn.close()
    print(
        f"Built {DB_PATH} from {SEED_PATH} — open it in DB Browser for SQLite to edit."
    )


if __name__ == "__main__":
    main()
