def test_list_families(client, make_family):
    family_a = make_family(slug="test.family-a")
    family_b = make_family(slug="test.family-b")

    response = client.get("/families")
    assert response.status_code == 200
    data = response.json()["data"]
    assert {item["id"] for item in data} == {family_a.slug, family_b.slug}
    assert all(item["type"] == "families" for item in data)


def test_get_family(client, make_person, make_family, make_event):
    father = make_person(slug="test.father")
    mother = make_person(slug="test.mother")
    child = make_person(slug="test.child")
    married = make_event(year=1741)
    family = make_family(
        father=father, mother=mother, children=[child], married=married
    )

    response = client.get(f"/families/{family.slug}")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["attributes"]["married"]["year"] == 1741
    assert body["relationships"]["father"]["data"] == {
        "type": "people",
        "id": "test.father",
    }
    assert body["relationships"]["mother"]["data"] == {
        "type": "people",
        "id": "test.mother",
    }
    assert body["relationships"]["children"]["data"] == [
        {"type": "people", "id": "test.child"}
    ]


def test_get_family_not_found(client):
    response = client.get("/families/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_include_people_returns_bare_resources(client, make_person, make_family):
    father = make_person(slug="test.father")
    mother = make_person(slug="test.mother")
    child = make_person(slug="test.child")
    family = make_family(father=father, mother=mother, children=[child])

    response = client.get(f"/families/{family.slug}?include=people")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 3
    ids = {item["id"] for item in included}
    assert ids == {"test.father", "test.mother", "test.child"}
    assert all(item["type"] == "people" for item in included)
    assert all(item.get("relationships") is None for item in included)


def test_links_self(client, make_family):
    family = make_family(slug="test.family")

    response = client.get(f"/families/{family.slug}")
    self_link = response.json()["data"]["links"]["self"]
    assert self_link.endswith(f"/families/{family.slug}")
