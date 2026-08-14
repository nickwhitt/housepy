from pyvis.network import Network

from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.house import House
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title
from scripts.export_graph import (
    FAMILY_COLOR,
    HOUSE_COLORS,
    TITLE_COLOR,
    _apply_colors,
    _house_colors,
    _house_line,
    _root_house,
    _title_tooltip,
    build_graph,
)


def _person(
    slug="test.person",
    birth_year=1900,
    death_year=None,
    sex=None,
    house=None,
    birth_house=None,
    titles=None,
):
    return Person(
        slug=slug,
        name=Name(given="Test"),
        birth=Event(birth_year),
        death=Event(death_year) if death_year else None,
        titles=titles or [],
        house=house,
        birth_house=birth_house,
        sex=sex,
    )


def _family(
    slug="test.family",
    father=None,
    mother=None,
    children=None,
    married_year=None,
    divorced_year=None,
):
    return Family(
        slug=slug,
        father=father,
        mother=mother,
        children=children or [],
        married=Event(married_year) if married_year else None,
        divorced=Event(divorced_year) if divorced_year else None,
    )


# ---------- person label/shape (via build_graph, family is just a carrier) ----------


def test_person_label_shows_birth_and_death_years():
    person = _person(birth_year=1719, death_year=1790)
    graph = build_graph(
        {person.slug: person}, {}, {}, [_family(children=[person.slug])]
    )
    assert graph.nodes[person.slug]["label"].endswith("1719-1790")


def test_person_label_shows_only_birth_year_when_living():
    person = _person(birth_year=1719)
    graph = build_graph(
        {person.slug: person}, {}, {}, [_family(children=[person.slug])]
    )
    year_line = graph.nodes[person.slug]["label"].split("\n")[-1]
    assert year_line == "1719"


def test_person_shape_male_is_sharp_box():
    person = _person(sex="male")
    graph = build_graph(
        {person.slug: person}, {}, {}, [_family(children=[person.slug])]
    )
    node = graph.nodes[person.slug]
    assert node["shape"] == "box"
    assert node["shapeProperties"]["borderRadius"] == 0


def test_person_shape_female_is_rounded_box():
    person = _person(sex="female")
    graph = build_graph(
        {person.slug: person}, {}, {}, [_family(children=[person.slug])]
    )
    node = graph.nodes[person.slug]
    assert node["shape"] == "box"
    assert node["shapeProperties"]["borderRadius"] == 20


def test_person_shape_unset_sex_is_diamond():
    person = _person(sex=None)
    graph = build_graph(
        {person.slug: person}, {}, {}, [_family(children=[person.slug])]
    )
    assert graph.nodes[person.slug]["shape"] == "diamond"


def test_person_tooltip_shows_house_name():
    house = House(slug="test.house", name="Test House")
    person = _person(house=house.slug)
    graph = build_graph(
        {person.slug: person},
        {},
        {house.slug: house},
        [_family(children=[person.slug])],
    )
    assert "House: Test House" in graph.nodes[person.slug]["title"]


def test_person_tooltip_shows_unrecorded_when_house_unset():
    person = _person(house=None)
    graph = build_graph(
        {person.slug: person}, {}, {}, [_family(children=[person.slug])]
    )
    assert "House: unrecorded" in graph.nodes[person.slug]["title"]


def test_house_line_appends_birth_house_when_set_and_different():
    house = House(slug="test.house", name="Windsor")
    birth_house = House(slug="test.birth-house", name="Saxe-Coburg and Gotha")
    person = _person(house=house.slug, birth_house=birth_house.slug)
    line = _house_line(person, {house.slug: house, birth_house.slug: birth_house})
    assert line == "House: Windsor (Saxe-Coburg and Gotha by birth)"


def test_house_line_omits_birth_house_when_unset():
    house = House(slug="test.house", name="Windsor")
    person = _person(house=house.slug)
    assert _house_line(person, {house.slug: house}) == "House: Windsor"


def test_person_appearing_in_multiple_families_gets_single_node():
    grandparent = _person(slug="test.grandparent")
    parent = _person(slug="test.parent")
    child = _person(slug="test.child")
    people = {p.slug: p for p in [grandparent, parent, child]}
    families = [
        _family(slug="test.family-1", father=grandparent.slug, children=[parent.slug]),
        _family(slug="test.family-2", father=parent.slug, children=[child.slug]),
    ]
    graph = build_graph(people, {}, {}, families)
    # 2 families + 3 people — parent isn't duplicated despite appearing as both
    # a child in family-1 and a father in family-2.
    assert graph.number_of_nodes() == 5


# ---------- title nodes ----------


def test_title_tooltip_shows_created_and_abolished():
    title = Title(
        slug="test.title",
        name="Test Title",
        created=Event(1567),
        abolished=Event(1806, 8, 14),
    )
    assert _title_tooltip(title) == "Created: 1567\nAbolished: 14 Aug 1806"


def test_title_tooltip_shows_only_abolished_when_created_unset():
    title = Title(slug="test.title", name="Test Title", abolished=Event(1806, 8, 14))
    assert _title_tooltip(title) == "Abolished: 14 Aug 1806"


def test_title_tooltip_empty_when_unset():
    title = Title(slug="test.title", name="Test Title")
    assert _title_tooltip(title) == ""


def test_title_node_tooltip_reflects_lifespan():
    title = Title(slug="test.title", name="Test Title", abolished=Event(1806, 8, 14))
    tenure = Tenure(title=title.slug, start=Event(1790))
    person = _person(titles=[tenure])
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    assert graph.nodes[title.slug]["title"] == "Abolished: 14 Aug 1806"


# ---------- tenure edges ----------


def test_tenure_edge_uses_explicit_end_when_set():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1790), end=Event(1806))
    person = _person(birth_year=1753, death_year=1830, titles=[tenure])
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "1790 - 1806"


def test_tenure_edge_falls_back_to_death_when_end_unset():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1806))
    person = _person(birth_year=1753, death_year=1830, titles=[tenure])
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "1806 - 1830"


def test_tenure_edge_falls_back_to_title_abolished_before_death():
    title = Title(slug="test.title", name="Test Title", abolished=Event(1806, 8, 14))
    tenure = Tenure(title=title.slug, start=Event(1790, 4, 6))
    person = _person(birth_year=1753, death_year=1830, titles=[tenure])
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "6 Apr 1790 - 14 Aug 1806"


def test_tenure_edge_falls_back_to_death_when_it_precedes_title_abolished():
    # An earlier holder who died before the title was later abolished under
    # their successor (Ludwig IX, d. 1790, vs. Landgrave of Hesse-Darmstadt
    # abolished 1806) must not inherit the abolition date.
    title = Title(slug="test.title", name="Test Title", abolished=Event(1806, 8, 14))
    tenure = Tenure(title=title.slug, start=Event(1768, 10, 12))
    person = _person(
        birth_year=1719, death_year=1790, titles=[tenure]
    )  # dies before title.abolished
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "12 Oct 1768 - 1790"


def test_tenure_edge_shows_only_start_for_living_open_tenure():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1806))
    person = _person(birth_year=1753, titles=[tenure])  # no death recorded
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "1806"


def test_tenure_edge_dashed_when_pretense():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1800), pretense=True)
    person = _person(titles=[tenure])
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    assert graph.edges[title.slug, person.slug, 0]["dashes"] is True


def test_regent_edge_added_when_regent_for_set():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1800), regent_for="test.monarch")
    person = _person(slug="test.regent", titles=[tenure])
    graph = build_graph(
        {person.slug: person},
        {title.slug: title},
        {},
        [_family(children=[person.slug])],
    )
    edge = graph.edges["test.regent", "test.monarch", 0]
    assert edge["label"] == "regent"


def test_shared_title_creates_single_node_with_both_edges():
    title = Title(slug="test.title", name="Test Title")
    holder1 = _person(
        slug="test.holder1",
        birth_year=1670,
        death_year=1720,
        titles=[Tenure(title=title.slug, start=Event(1700), end=Event(1720))],
    )
    holder2 = _person(
        slug="test.holder2",
        birth_year=1700,
        titles=[Tenure(title=title.slug, start=Event(1720))],
    )
    people = {holder1.slug: holder1, holder2.slug: holder2}
    family = _family(children=[holder1.slug, holder2.slug])
    graph = build_graph(people, {title.slug: title}, {}, [family])
    assert graph.out_degree(title.slug) == 2
    assert graph.has_edge(title.slug, holder1.slug)
    assert graph.has_edge(title.slug, holder2.slug)


# ---------- family label/edges ----------


def test_family_label_shows_marriage_year_only():
    family = _family(married_year=1741)
    graph = build_graph({}, {}, {}, [family])
    assert graph.nodes[family.slug]["label"] == "1741"


def test_family_label_shows_marriage_and_divorce_range():
    family = _family(married_year=1741, divorced_year=1755)
    graph = build_graph({}, {}, {}, [family])
    assert graph.nodes[family.slug]["label"] == "1741-1755"


def test_family_label_falls_back_to_unknown():
    family = _family()
    graph = build_graph({}, {}, {}, [family])
    assert graph.nodes[family.slug]["label"] == "unknown"


def test_family_parent_edges_are_dashed():
    father = _person(slug="test.father")
    mother = _person(slug="test.mother")
    family = _family(father=father.slug, mother=mother.slug)
    people = {father.slug: father, mother.slug: mother}
    graph = build_graph(people, {}, {}, [family])
    assert graph.edges[family.slug, father.slug, 0]["dashes"] is True
    assert graph.edges[family.slug, mother.slug, 0]["dashes"] is True


def test_family_child_edges_are_not_dashed():
    child = _person(slug="test.child")
    family = _family(children=[child.slug])
    graph = build_graph({child.slug: child}, {}, {}, [family])
    assert "dashes" not in graph.edges[family.slug, child.slug, 0]


# ---------- house colors ----------


def test_house_colors_empty_when_no_people():
    assert _house_colors({}, {}) == {}


def test_house_colors_ignores_people_without_house():
    person = _person(house=None)
    assert _house_colors({person.slug: person}, {}) == {}


def test_house_colors_assigned_in_sorted_order_not_insertion_order():
    people = {
        "p1": _person(slug="p1", house="test.house-z"),
        "p2": _person(slug="p2", house="test.house-a"),
    }
    colors = _house_colors(people, {})
    assert colors["test.house-a"] == (HOUSE_COLORS[0], False)
    assert colors["test.house-z"] == (HOUSE_COLORS[1], False)


def test_house_colors_wrap_around_reuses_hue_but_flags_it_dashed():
    house_slugs = [
        f"test.house-{letter}" for letter in "abcdefghi"
    ]  # 9 houses > 8-slot ramp
    people = {
        f"p{i}": _person(slug=f"p{i}", house=house)
        for i, house in enumerate(house_slugs)
    }
    colors = _house_colors(people, {})
    # 9th root reuses the 1st root's hue (only 8 slots)...
    assert colors["test.house-a"][0] == HOUSE_COLORS[0]
    assert colors["test.house-i"][0] == HOUSE_COLORS[0]
    # ...but isn't a true duplicate: the dash flag tells them apart.
    assert colors["test.house-a"][1] is False
    assert colors["test.house-i"][1] is True


def test_house_colors_third_pass_returns_to_solid():
    # 17 houses: index 16 is the 3rd pass through the 8-slot ramp, which
    # wraps the 2-band dash cycle back to solid — an exact repeat of the
    # 1st root's (color, dashed) pair. Documents the accepted limit rather
    # than asserting it should be avoided.
    house_slugs = [f"test.house-{i:02d}" for i in range(17)]
    people = {
        f"p{i}": _person(slug=f"p{i}", house=house)
        for i, house in enumerate(house_slugs)
    }
    colors = _house_colors(people, {})
    expected = (HOUSE_COLORS[0], False)
    assert colors["test.house-00"] == expected
    assert colors["test.house-16"] == expected


def test_house_colors_keyed_by_root_not_cadet_branch():
    root = House(slug="test.hesse", name="Hesse")
    cadet = House(slug="test.hesse-darmstadt", name="Hesse-Darmstadt", parent=root.slug)
    person = _person(house=cadet.slug)
    colors = _house_colors({person.slug: person}, {root.slug: root, cadet.slug: cadet})
    assert colors == {root.slug: (HOUSE_COLORS[0], False)}


def test_house_colors_keyed_by_predecessor_not_renamed_house():
    predecessor = House(slug="test.battenberg", name="Battenberg")
    renamed = House(
        slug="test.mountbatten", name="Mountbatten", renamed_from=predecessor.slug
    )
    person = _person(house=renamed.slug)
    colors = _house_colors(
        {person.slug: person}, {predecessor.slug: predecessor, renamed.slug: renamed}
    )
    assert colors == {predecessor.slug: (HOUSE_COLORS[0], False)}


def test_root_house_returns_slug_unchanged_when_no_parent_or_rename():
    house = House(slug="test.house", name="Test House")
    assert _root_house(house.slug, {house.slug: house}) == house.slug


def test_root_house_returns_slug_unchanged_when_unknown():
    assert _root_house("test.unknown", {}) == "test.unknown"


def test_root_house_walks_multiple_hops_mixing_parent_and_renamed_from():
    root = House(slug="test.hesse", name="Hesse")
    cadet = House(slug="test.hesse-darmstadt", name="Hesse-Darmstadt", parent=root.slug)
    renamed = House(
        slug="test.mountbatten", name="Mountbatten", renamed_from=cadet.slug
    )
    houses = {root.slug: root, cadet.slug: cadet, renamed.slug: renamed}
    assert _root_house(renamed.slug, houses) == root.slug


def test_root_house_stops_instead_of_looping_on_a_cycle():
    a = House(slug="test.a", name="A", parent="test.b")
    b = House(slug="test.b", name="B", parent="test.a")
    houses = {a.slug: a, b.slug: b}
    assert _root_house(a.slug, houses) in {a.slug, b.slug}


# ---------- selection colors ----------
# vis-network falls back to a hardcoded blue for a node's `color.highlight`
# (used on selection) when it isn't set explicitly — these confirm
# `_apply_colors` always sets it to match the node's own background/border.


def test_apply_colors_person_highlight_matches_base_color():
    house = House(slug="test.house", name="Test House")
    person = _person(house=house.slug)
    network = Network()
    network.add_node(person.slug, group="person")
    _apply_colors(
        network,
        {person.slug: person},
        {house.slug: house},
        {house.slug: ("#123456", False)},
    )
    color = network.nodes[0]["color"]
    assert color["highlight"] == {
        "background": color["background"],
        "border": color["border"],
    }


def test_apply_colors_person_not_dashed_by_default():
    house = House(slug="test.house", name="Test House")
    person = _person(house=house.slug)
    network = Network()
    network.add_node(person.slug, group="person")
    _apply_colors(
        network,
        {person.slug: person},
        {house.slug: house},
        {house.slug: ("#123456", False)},
    )
    assert "shapeProperties" not in network.nodes[0]


def test_apply_colors_person_dashed_on_second_band():
    house = House(slug="test.house", name="Test House")
    person = _person(house=house.slug)
    network = Network()
    network.add_node(person.slug, group="person")
    _apply_colors(
        network,
        {person.slug: person},
        {house.slug: house},
        {house.slug: ("#123456", True)},
    )
    assert network.nodes[0]["shapeProperties"]["borderDashes"] is True


def test_apply_colors_person_dashed_merges_with_existing_shape_properties():
    house = House(slug="test.house", name="Test House")
    person = _person(house=house.slug, sex="male")
    network = Network()
    network.add_node(person.slug, group="person", shapeProperties={"borderRadius": 0})
    _apply_colors(
        network,
        {person.slug: person},
        {house.slug: house},
        {house.slug: ("#123456", True)},
    )
    node = network.nodes[0]
    assert node["shapeProperties"]["borderRadius"] == 0
    assert node["shapeProperties"]["borderDashes"] is True


def test_apply_colors_title_highlight_matches_base_color():
    network = Network()
    network.add_node("test.title", group="title")
    _apply_colors(network, {}, {}, {})
    assert network.nodes[0]["color"] == {**TITLE_COLOR, "highlight": TITLE_COLOR}


def test_apply_colors_family_highlight_matches_base_color():
    network = Network()
    network.add_node("test.family", group="family")
    _apply_colors(network, {}, {}, {})
    assert network.nodes[0]["color"] == {**FAMILY_COLOR, "highlight": FAMILY_COLOR}
