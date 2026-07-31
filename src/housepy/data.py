from housepy.db.loader import get_connection, materialize

# Kept alive: a free baseline for future runtime querying/filtering, unused
# for now — reads are still served from the materialized objects below.
connection = get_connection()
_loaded = materialize(connection)

people = _loaded.people
titles = _loaded.titles
families = _loaded.families
houses = _loaded.houses
