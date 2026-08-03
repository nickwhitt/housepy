import re
from pathlib import Path

from networkx import MultiDiGraph
from pyvis.network import Network
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from housepy.db.loader import list_families, list_people, list_titles, load_seed_data
from housepy.db.tables import Base
from housepy.models.family import Family
from housepy.models.person import Person
from housepy.models.title import Title

OUTPUT_PATH = Path("docs/graph.html")

# Fixed-order categorical ramp (dataviz skill's validated 8-hue set — CVD-safe
# adjacent pairs) for house identity, shown as each person node's border.
# People without a recorded house fall back to a neutral, off-ramp gray.
HOUSE_COLORS = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]
NO_HOUSE_COLOR = "#898781"

# Structural chrome for title/family nodes — muted relative to the vivid house
# ramp above (so neither reads as "a house"), but split warm vs. cool so the
# two are easy to tell apart at a glance, unlike an earlier same-temperature
# sage/taupe pairing that read as one color.
TITLE_COLOR = {"background": "#f6ead2", "border": "#b5793e"}  # warm ochre
FAMILY_COLOR = {"background": "#e6ecf5", "border": "#5c6f95"}  # cool slate-blue

# Standard pedigree-chart shapes (square/circle/diamond for male/female/
# unknown), adapted to vis-network's actual sizing behavior: both known-sex
# shapes stay "box" — it fits width/height to the label independently,
# unlike "circle" (forces width == height, so a long name blows its
# diameter out) or "ellipse" (fits, but a long single-line name still
# reads oddly against a two-line label) — and are told apart purely by
# corner rounding instead: sharp 90° corners for male, a rounded/pill-like
# box for female. `shapeProperties.borderRadius` is a real vis-network node
# option (confirmed in the bundled vis-network source: default 6, valid
# range 0-20), passed straight through by pyvis's Node class untouched —
# unlike the `color` parameter, it isn't dropped when `group` is also set.
# Unset sex falls back to "diamond", the one shape vis-network draws with
# the label outside, so an unrecorded sex visibly stands out rather than
# blending in.
PERSON_SHAPE = {
    "male": {"shape": "box", "shapeProperties": {"borderRadius": 0}},
    "female": {"shape": "box", "shapeProperties": {"borderRadius": 20}},
}


def _build_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    event.listens_for(engine, "connect")(
        lambda dbapi_conn, _: dbapi_conn.execute("PRAGMA foreign_keys=ON")
    )
    Base.metadata.create_all(engine)
    load_seed_data(engine)
    return engine


def _house_colors(people: dict[str, Person]) -> dict[str, str]:
    houses = sorted({person.house for person in people.values() if person.house})
    return {
        house: HOUSE_COLORS[i % len(HOUSE_COLORS)] for i, house in enumerate(houses)
    }


def _add_person_node(
    graph: MultiDiGraph, person: Person, titles: dict[str, Title]
) -> None:
    if person.slug in graph.nodes:
        return

    lifespan = [
        occurrence
        for occurrence in (person.birth, person.death)
        if occurrence is not None
    ]
    death_lines = "\n† ".join(str(occurrence) for occurrence in lifespan)
    graph.add_node(
        person.slug,
        label=f"{person}\n{'-'.join(str(occurrence.year) for occurrence in lifespan)}",
        title=(
            f"{person.name.given or person.name.first}\n"
            f"* {death_lines} (age {person.age})"
        ),
        group="person",
        **PERSON_SHAPE.get(person.sex or "", {"shape": "diamond"}),
    )

    for tenure in person.titles:
        title = titles[tenure.title]
        if title.slug not in graph.nodes:
            graph.add_node(title.slug, label=str(title), group="title", shape="box")

        # An open-ended tenure (no recorded end) ran until the holder's death — a
        # display-only fallback, not written back to the tenure record. Still None
        # for a living, currently-tenured holder.
        end = tenure.end or person.death
        reign = " - ".join(
            str(occurrence) for occurrence in (tenure.start, end) if occurrence
        )
        graph.add_edge(
            title.slug,
            person.slug,
            label=str(tenure.start.year),
            title=f"tenure: {reign}",
            dashes=tenure.pretense,
        )

        if tenure.regent_for is not None:
            graph.add_edge(person.slug, tenure.regent_for, label="regent", dashes=True)


def _add_family_node(
    graph: MultiDiGraph,
    family: Family,
    people: dict[str, Person],
    titles: dict[str, Title],
) -> None:
    # Mirrors _add_person_node's label exactly: bare years joined by "-",
    # symbols reserved for the tooltip. A family always has at most two
    # dates (married/divorced), same shape as a person's birth/death.
    marriage_span = [
        occurrence
        for occurrence in (family.married, family.divorced)
        if occurrence is not None
    ]
    label = "-".join(str(occurrence.year) for occurrence in marriage_span) or "unknown"

    graph.add_node(
        family.slug,
        label=label,
        title="\n".join(
            filter(
                None,
                [
                    f"⚭ {family.married}" if family.married else None,
                    f"⚮ {family.divorced}" if family.divorced else None,
                ],
            )
        ),
        group="family",
        # "dot" is fixed-size and label-outside — family's label is already
        # short ("1741-1755"), and a fixed size means it can't grow with text
        # the way ellipse/box do, so it stays visually distinct from person
        # nodes regardless of label length.
        shape="dot",
    )

    for parent_slug in filter(None, [family.father, family.mother]):
        _add_person_node(graph, people[parent_slug], titles)
        graph.add_edge(family.slug, parent_slug, dashes=True)

    for child_slug in family.children:
        _add_person_node(graph, people[child_slug], titles)
        graph.add_edge(family.slug, child_slug)


def build_graph(
    people: dict[str, Person], titles: dict[str, Title], families: list[Family]
) -> MultiDiGraph:
    graph = MultiDiGraph()
    for family in families:
        _add_family_node(graph, family, people, titles)
    return graph


def _apply_colors(
    network: Network, people: dict[str, Person], house_colors: dict[str, str]
) -> None:
    # pyvis' add_node() silently drops an explicit `color` whenever `group` is
    # also set (it assumes the group owns styling in that case) — so colors are
    # applied here, as a pass over the already-built pyvis nodes, instead.
    for node in network.nodes:
        if node["group"] == "person":
            house = people[node["id"]].house
            node["color"] = {
                "background": "#ffffff",
                "border": house_colors.get(house or "", NO_HOUSE_COLOR),
            }
            node["borderWidth"] = 3
        elif node["group"] == "title":
            node["color"] = TITLE_COLOR
        elif node["group"] == "family":
            node["color"] = FAMILY_COLOR


def main() -> None:
    engine = _build_engine()
    with Session(engine) as session:
        people = {person.slug: person for person in list_people(session)}
        titles = {title.slug: title for title in list_titles(session)}
        families = list_families(session)

    graph = build_graph(people, titles, families)

    # select_menu=True would also wire pyvis' bundled neighbourhoodHighlight
    # click handler (confirmed in pyvis' own template.html — the two aren't
    # separable), which has a known bug: it grays out the whole graph after
    # the first selection instead of resetting cleanly. Left off since we
    # don't use the node-search dropdown it brings, and it's third-party
    # template JS not worth patching for that.
    # "100%" wouldn't work here — pyvis' #mynetwork div has no ancestor
    # (html/body) with an explicit height, and CSS percentage heights need
    # that chain or they collapse. "vh" is relative to the viewport itself,
    # not a parent element, so it doesn't have that dependency.
    network = Network(height="100vh", directed=True, cdn_resources="remote")
    network.set_options("""
    var options = {
      "nodes": {
        "margin": { "top": 10, "right": 14, "bottom": 10, "left": 14 }
      },
      "edges": {
        "arrows": {
          "to": { "enabled": true, "scaleFactor": 0 },
          "middle": { "enabled": true, "scaleFactor": 0 },
          "from": { "enabled": true, "scaleFactor": 0 }
        }
      }
    }
    """)
    network.from_nx(graph)
    _apply_colors(network, people, _house_colors(people))

    # pyvis' template renders `<center><h1>{{heading}}</h1></center>` (twice)
    # unconditionally — an empty heading="" still leaves two blank <h1>
    # blocks reserving vertical space above the graph, which is what was
    # eating into the 100vh canvas. No constructor flag suppresses it, so
    # it's stripped here rather than fought in the template.
    html = re.sub(
        r"<center>\s*<h1>\s*</h1>\s*</center>\s*", "", network.generate_html()
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)


if __name__ == "__main__":
    main()
