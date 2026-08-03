import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("housepy.db")
SEED_PATH = Path("src/housepy/db/seed.sql")

# Fixed order for readable, stable diffs (iterdump() defaults to alphabetical).
TABLE_ORDER = [
    "events",
    "houses",
    "titles",
    "people",
    "tenures",
    "families",
    "family_children",
]


def main() -> None:
    conn = sqlite3.connect(DB_PATH)

    bad_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    if bad_rows:
        print("PRAGMA foreign_key_check found broken references:")
        for row in bad_rows:
            print(f"  {row}")
        sys.exit(1)

    inserts_by_table: dict[str, list[str]] = {table: [] for table in TABLE_ORDER}
    for line in conn.iterdump():
        for table in TABLE_ORDER:
            if line.startswith(f'INSERT INTO "{table}"'):
                inserts_by_table[table].append(line)
                break
    conn.close()

    lines = ["BEGIN TRANSACTION;"]
    for table in TABLE_ORDER:
        lines.extend(inserts_by_table[table])
    lines.append("COMMIT;")

    SEED_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {SEED_PATH} — review the diff before committing.")


if __name__ == "__main__":
    main()
