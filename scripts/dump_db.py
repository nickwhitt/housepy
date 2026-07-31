import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("housepy.db")
SEED_PATH = Path("src/housepy/db/seed.sql")

# CREATE TABLE and INSERT statements are both emitted in this order so every
# FK target table already exists as a schema object by the time its child
# table's rows are inserted. Deferred FK checking (DEFERRABLE INITIALLY
# DEFERRED) only defers the row-level check to COMMIT — the referenced
# table still has to exist when the INSERT runs, which iterdump()'s default
# alphabetical-per-table ordering doesn't guarantee.
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

    schema_by_table = dict(
        conn.execute(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    )
    inserts_by_table: dict[str, list[str]] = {table: [] for table in TABLE_ORDER}
    for line in conn.iterdump():
        for table in TABLE_ORDER:
            if line.startswith(f'INSERT INTO "{table}"'):
                inserts_by_table[table].append(line)
                break
    conn.close()

    lines = ["PRAGMA foreign_keys = ON;", ""]
    for table in TABLE_ORDER:
        lines.append(schema_by_table[table] + ";")
        lines.append("")
    lines.append("BEGIN TRANSACTION;")
    for table in TABLE_ORDER:
        lines.extend(inserts_by_table[table])
    lines.append("COMMIT;")

    SEED_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {SEED_PATH} — review the diff before committing.")


if __name__ == "__main__":
    main()
