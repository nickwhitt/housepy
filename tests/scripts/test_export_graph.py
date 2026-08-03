from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title
from scripts.export_graph import HOUSE_COLORS, _house_colors, build_graph


def _person(
    slug="test.person",
    birth_year=1900,
    death_year=None,
    sex=None,
    house=None,
    titles=None,
):
    return Person(
        slug=slug,
        name=Name(given="Test"),
        birth=Event(birth_year),
        death=Event(death_year) if death_year else None,
        titles=titles or [],
        house=house,
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
    graph = build_graph({person.slug: person}, {}, [_family(children=[person.slug])])
    assert graph.nodes[person.slug]["label"].endswith("1719-1790")


def test_person_label_shows_only_birth_year_when_living():
    person = _person(birth_year=1719)
    graph = build_graph({person.slug: person}, {}, [_family(children=[person.slug])])
    year_line = graph.nodes[person.slug]["label"].split("\n")[-1]
    assert year_line == "1719"


def test_person_shape_male_is_sharp_box():
    person = _person(sex="male")
    graph = build_graph({person.slug: person}, {}, [_family(children=[person.slug])])
    node = graph.nodes[person.slug]
    assert node["shape"] == "box"
    assert node["shapeProperties"]["borderRadius"] == 0


def test_person_shape_female_is_rounded_box():
    person = _person(sex="female")
    graph = build_graph({person.slug: person}, {}, [_family(children=[person.slug])])
    node = graph.nodes[person.slug]
    assert node["shape"] == "box"
    assert node["shapeProperties"]["borderRadius"] == 20


def test_person_shape_unset_sex_is_diamond():
    person = _person(sex=None)
    graph = build_graph({person.slug: person}, {}, [_family(children=[person.slug])])
    assert graph.nodes[person.slug]["shape"] == "diamond"


def test_person_appearing_in_multiple_families_gets_single_node():
    grandparent = _person(slug="test.grandparent")
    parent = _person(slug="test.parent")
    child = _person(slug="test.child")
    people = {p.slug: p for p in [grandparent, parent, child]}
    families = [
        _family(slug="test.family-1", father=grandparent.slug, children=[parent.slug]),
        _family(slug="test.family-2", father=parent.slug, children=[child.slug]),
    ]
    graph = build_graph(people, {}, families)
    # 2 families + 3 people — parent isn't duplicated despite appearing as both
    # a child in family-1 and a father in family-2.
    assert graph.number_of_nodes() == 5


# ---------- tenure edges ----------


def test_tenure_edge_uses_explicit_end_when_set():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1790), end=Event(1806))
    person = _person(birth_year=1753, death_year=1830, titles=[tenure])
    graph = build_graph(
        {person.slug: person}, {title.slug: title}, [_family(children=[person.slug])]
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "tenure: 1790 - 1806"


def test_tenure_edge_falls_back_to_death_when_end_unset():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1806))
    person = _person(birth_year=1753, death_year=1830, titles=[tenure])
    graph = build_graph(
        {person.slug: person}, {title.slug: title}, [_family(children=[person.slug])]
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "tenure: 1806 - 1830"


def test_tenure_edge_shows_only_start_for_living_open_tenure():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1806))
    person = _person(birth_year=1753, titles=[tenure])  # no death recorded
    graph = build_graph(
        {person.slug: person}, {title.slug: title}, [_family(children=[person.slug])]
    )
    edge = graph.edges[title.slug, person.slug, 0]
    assert edge["title"] == "tenure: 1806"


def test_tenure_edge_dashed_when_pretense():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1800), pretense=True)
    person = _person(titles=[tenure])
    graph = build_graph(
        {person.slug: person}, {title.slug: title}, [_family(children=[person.slug])]
    )
    assert graph.edges[title.slug, person.slug, 0]["dashes"] is True


def test_regent_edge_added_when_regent_for_set():
    title = Title(slug="test.title", name="Test Title")
    tenure = Tenure(title=title.slug, start=Event(1800), regent_for="test.monarch")
    person = _person(slug="test.regent", titles=[tenure])
    graph = build_graph(
        {person.slug: person}, {title.slug: title}, [_family(children=[person.slug])]
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
    graph = build_graph(people, {title.slug: title}, [family])
    assert graph.out_degree(title.slug) == 2
    assert graph.has_edge(title.slug, holder1.slug)
    assert graph.has_edge(title.slug, holder2.slug)


# ---------- family label/edges ----------


def test_family_label_shows_marriage_year_only():
    family = _family(married_year=1741)
    graph = build_graph({}, {}, [family])
    assert graph.nodes[family.slug]["label"] == "1741"


def test_family_label_shows_marriage_and_divorce_range():
    family = _family(married_year=1741, divorced_year=1755)
    graph = build_graph({}, {}, [family])
    assert graph.nodes[family.slug]["label"] == "1741-1755"


def test_family_label_falls_back_to_unknown():
    family = _family()
    graph = build_graph({}, {}, [family])
    assert graph.nodes[family.slug]["label"] == "unknown"


def test_family_parent_edges_are_dashed():
    father = _person(slug="test.father")
    mother = _person(slug="test.mother")
    family = _family(father=father.slug, mother=mother.slug)
    people = {father.slug: father, mother.slug: mother}
    graph = build_graph(people, {}, [family])
    assert graph.edges[family.slug, father.slug, 0]["dashes"] is True
    assert graph.edges[family.slug, mother.slug, 0]["dashes"] is True


def test_family_child_edges_are_not_dashed():
    child = _person(slug="test.child")
    family = _family(children=[child.slug])
    graph = build_graph({child.slug: child}, {}, [family])
    assert "dashes" not in graph.edges[family.slug, child.slug, 0]


# ---------- house colors ----------


def test_house_colors_empty_when_no_people():
    assert _house_colors({}) == {}


def test_house_colors_ignores_people_without_house():
    person = _person(house=None)
    assert _house_colors({person.slug: person}) == {}


def test_house_colors_assigned_in_sorted_order_not_insertion_order():
    people = {
        "p1": _person(slug="p1", house="test.house-z"),
        "p2": _person(slug="p2", house="test.house-a"),
    }
    colors = _house_colors(people)
    assert colors["test.house-a"] == HOUSE_COLORS[0]
    assert colors["test.house-z"] == HOUSE_COLORS[1]


def test_house_colors_wrap_around_past_ramp_length():
    house_slugs = [
        f"test.house-{letter}" for letter in "abcdefghi"
    ]  # 9 houses > 8-slot ramp
    people = {
        f"p{i}": _person(slug=f"p{i}", house=house)
        for i, house in enumerate(house_slugs)
    }
    colors = _house_colors(people)
    assert colors["test.house-a"] == HOUSE_COLORS[0]
    assert colors["test.house-i"] == HOUSE_COLORS[0]
