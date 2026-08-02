def test_list_people(client, make_person):
    make_person(slug="test.alice")
    make_person(slug="test.bob")

    response = client.get("/people")
    assert response.status_code == 200
    data = response.json()["data"]
    assert {item["id"] for item in data} == {"test.alice", "test.bob"}
    assert all(item["type"] == "people" for item in data)


def test_get_person_with_title(client, make_person, make_title, make_tenure):
    title = make_title(slug="test.duke")
    person = make_person(slug="test.alice")
    make_tenure(person=person, title=title)

    response = client.get(f"/people/{person.slug}")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["relationships"]["titles"]["data"] == [
        {"type": "titles", "id": "test.duke"}
    ]


def test_get_person_with_no_titles(client, make_person):
    person = make_person(slug="test.alice")

    response = client.get(f"/people/{person.slug}")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["relationships"]["titles"]["data"] == []


def test_get_person_not_found(client):
    response = client.get("/people/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_include_titles_returns_bare_resource(
    client, make_person, make_title, make_tenure
):
    title = make_title(slug="test.duke", name="Duke of Test")
    person = make_person(slug="test.alice")
    make_tenure(person=person, title=title)

    response = client.get(f"/people/{person.slug}?include=titles")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 1
    assert included[0]["type"] == "titles"
    assert included[0]["id"] == "test.duke"
    assert included[0].get("relationships") is None


def test_include_titles_absent_when_no_titles(client, make_person):
    person = make_person(slug="test.alice")

    response = client.get(f"/people/{person.slug}?include=titles")
    assert response.status_code == 200
    assert response.json().get("included") is None


def test_include_unrecognized_type_is_inert(client):
    response = client.get("/people?include=bogus")
    assert response.status_code == 200
    assert response.json().get("included") is None


def test_get_person_families_as_father(client, make_person, make_family):
    father = make_person(slug="test.father")
    mother = make_person(slug="test.mother")
    family = make_family(father=father, mother=mother)

    response = client.get(f"/people/{father.slug}")
    body = response.json()["data"]
    assert body["relationships"]["families"]["data"] == [
        {"type": "families", "id": family.slug}
    ]


def test_get_person_families_as_child(client, make_person, make_family):
    father = make_person(slug="test.father")
    mother = make_person(slug="test.mother")
    child = make_person(slug="test.child")
    family = make_family(father=father, mother=mother, children=[child])

    response = client.get(f"/people/{child.slug}")
    body = response.json()["data"]
    assert body["relationships"]["families"]["data"] == [
        {"type": "families", "id": family.slug}
    ]


def test_include_families_returns_bare_resource(client, make_person, make_family):
    father = make_person(slug="test.father")
    mother = make_person(slug="test.mother")
    family = make_family(father=father, mother=mother)

    response = client.get(f"/people/{mother.slug}?include=families")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 1
    assert included[0]["type"] == "families"
    assert included[0]["id"] == family.slug
    assert included[0].get("relationships") is None


def test_get_person_house(client, make_person, make_house):
    house = make_house(slug="test.house")
    person = make_person(slug="test.alice", house=house)

    response = client.get(f"/people/{person.slug}")
    body = response.json()["data"]
    assert body["relationships"]["house"]["data"] == {
        "type": "houses",
        "id": "test.house",
    }


def test_include_house_returns_bare_resource(client, make_person, make_house):
    house = make_house(slug="test.house")
    person = make_person(slug="test.alice", house=house)

    response = client.get(f"/people/{person.slug}?include=houses")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 1
    assert included[0]["type"] == "houses"
    assert included[0]["id"] == "test.house"
    assert included[0].get("relationships") is None


def test_links_self(client, make_person):
    person = make_person(slug="test.alice")

    response = client.get(f"/people/{person.slug}")
    self_link = response.json()["data"]["links"]["self"]
    assert self_link.endswith(f"/people/{person.slug}")
