import re
from pathlib import Path

from networkx import MultiDiGraph
from pyvis.network import Network
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from housepy.db.loader import (
    list_families,
    list_houses,
    list_people,
    list_titles,
    load_seed_data,
)
from housepy.db.tables import Base
from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.house import House
from housepy.models.person import Person
from housepy.models.title import Tenure, Title

OUTPUT_PATH = Path("docs/graph.html")

# Categorical ramp for house identity, shown as each person node's border.
# No recorded house falls back to a neutral gray.
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

# Muted title/family node colors, warm vs. cool so they're distinguishable
# from each other and from the vivid house ramp above.
TITLE_COLOR = {"background": "#f6ead2", "border": "#b5793e"}  # warm ochre
FAMILY_COLOR = {"background": "#e6ecf5", "border": "#5c6f95"}  # cool slate-blue

# Pedigree-chart shapes: sharp-cornered box (male) vs. rounded box (female,
# via shapeProperties.borderRadius); diamond fallback for unset sex.
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


def _root_house(slug: str, houses: dict[str, House]) -> str:
    """Walks `parent` (cadet branch) and `renamed_from` (same house, earlier
    name) links to the top of a house's lineage — both mean "this house
    descends from that one," just via different real-world mechanisms, so a
    rename and a true cadet branch both collapse toward the same root color.
    Stops instead of looping if the data has a cycle."""
    visited: set[str] = set()
    while slug not in visited:
        visited.add(slug)
        house = houses.get(slug)
        next_slug = (house.parent or house.renamed_from) if house else None
        if next_slug is None:
            return slug
        slug = next_slug
    return slug


def _house_colors(
    people: dict[str, Person], houses: dict[str, House]
) -> dict[str, str]:
    roots = sorted(
        {
            _root_house(person.house, houses)
            for person in people.values()
            if person.house
        }
    )
    return {root: HOUSE_COLORS[i % len(HOUSE_COLORS)] for i, root in enumerate(roots)}


def _house_line(person: Person, houses: dict[str, House]) -> str:
    house = houses[person.house].name if person.house else "unrecorded"
    if person.birth_house:
        return f"House: {house} ({houses[person.birth_house].name} by birth)"
    return f"House: {house}"


def _title_tooltip(title: Title) -> str:
    return "\n".join(
        filter(
            None,
            [
                f"Created: {title.created}" if title.created else None,
                f"Abolished: {title.abolished}" if title.abolished else None,
            ],
        )
    )


def _tenure_end(tenure: Tenure, title: Title, person: Person) -> Event | None:
    # Earliest of the two, not a fixed preference; compares raw
    # (year, month, day) since Event's own ordering raises on year-only dates.
    if tenure.end:
        return tenure.end
    candidates = [e for e in (title.abolished, person.death) if e is not None]
    return min(candidates, key=lambda e: (e.year, e.month, e.day), default=None)


def _add_person_node(
    graph: MultiDiGraph,
    person: Person,
    titles: dict[str, Title],
    houses: dict[str, House],
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
            f"* {death_lines} (age {person.age})\n"
            f"{_house_line(person, houses)}"
        ),
        group="person",
        **PERSON_SHAPE.get(person.sex or "", {"shape": "diamond"}),
    )

    for tenure in person.titles:
        title = titles[tenure.title]
        if title.slug not in graph.nodes:
            graph.add_node(
                title.slug,
                label=str(title),
                title=_title_tooltip(title),
                group="title",
                shape="box",
            )

        end = _tenure_end(tenure, title, person)
        reign = " - ".join(
            str(occurrence) for occurrence in (tenure.start, end) if occurrence
        )
        graph.add_edge(
            title.slug,
            person.slug,
            label=str(tenure.start.year),
            title=reign,
            dashes=tenure.pretense,
        )

        if tenure.regent_for is not None:
            graph.add_edge(person.slug, tenure.regent_for, label="regent", dashes=True)


def _add_family_node(
    graph: MultiDiGraph,
    family: Family,
    people: dict[str, Person],
    titles: dict[str, Title],
    houses: dict[str, House],
) -> None:
    # Bare years joined by "-"; symbols reserved for the tooltip.
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
        shape="dot",  # fixed-size, keeps family nodes visually distinct from people
    )

    for parent_slug in filter(None, [family.father, family.mother]):
        _add_person_node(graph, people[parent_slug], titles, houses)
        graph.add_edge(family.slug, parent_slug, dashes=True)

    for child_slug in family.children:
        _add_person_node(graph, people[child_slug], titles, houses)
        graph.add_edge(family.slug, child_slug)


def build_graph(
    people: dict[str, Person],
    titles: dict[str, Title],
    houses: dict[str, House],
    families: list[Family],
) -> MultiDiGraph:
    # Walks families only; a Person who is nobody's parent/child in any
    # Family row is never added (nor are their titles, since those edges
    # are also only built inside _add_person_node). Not handled: every
    # person in this dataset is expected to appear in at least one Family.
    graph = MultiDiGraph()
    for family in families:
        _add_family_node(graph, family, people, titles, houses)
    return graph


def _apply_colors(
    network: Network,
    people: dict[str, Person],
    houses: dict[str, House],
    house_colors: dict[str, str],
) -> None:
    # pyvis drops an explicit `color` when `group` is also set, so colors are
    # applied here instead, as a pass over the already-built pyvis nodes.
    for node in network.nodes:
        if node["group"] == "person":
            house = people[node["id"]].house
            root = _root_house(house, houses) if house else None
            color = {
                "background": "#ffffff",
                "border": house_colors.get(root or "", NO_HOUSE_COLOR),
            }
            node["color"] = {**color, "highlight": color}
            node["borderWidth"] = 3
        elif node["group"] == "title":
            node["color"] = {**TITLE_COLOR, "highlight": TITLE_COLOR}
        elif node["group"] == "family":
            node["color"] = {**FAMILY_COLOR, "highlight": FAMILY_COLOR}


def main() -> None:
    engine = _build_engine()
    with Session(engine) as session:
        people = {person.slug: person for person in list_people(session)}
        titles = {title.slug: title for title in list_titles(session)}
        houses = {house.slug: house for house in list_houses(session)}
        families = list_families(session)

    graph = build_graph(people, titles, houses, families)

    # neighborhood_highlight, not select_menu — see CLAUDE.local.md.
    # "100vh", not "100%" — #mynetwork has no ancestor with an explicit height.
    network = Network(
        height="100vh",
        directed=True,
        cdn_resources="remote",
        neighborhood_highlight=True,
    )
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
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -4000,
          "centralGravity": 0.3,
          "springLength": 120,
          "damping": 0.4,
          "avoidOverlap": 0.5
        },
        "minVelocity": 2
      }
    }
    """)
    network.from_nx(graph)
    _apply_colors(network, people, houses, _house_colors(people, houses))

    # Strips pyvis' blank <h1> heading blocks, which otherwise eat into the
    # 100vh canvas — no constructor flag suppresses them.
    html = re.sub(
        r"<center>\s*<h1>\s*</h1>\s*</center>\s*", "", network.generate_html()
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)


if __name__ == "__main__":
    main()
