FAMILY_SLUG = "hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1"


def test_list_people(client):
    response = client.get("/people")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 3
    assert all(item["type"] == "people" for item in data)


def test_get_person_with_title(client):
    response = client.get("/people/hesse-darmstadt.ludwig-ix")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["relationships"]["titles"]["data"] == [
        {"type": "titles", "id": "hesse-darmstadt.landgrave"}
    ]


def test_get_person_with_no_titles(client):
    response = client.get("/people/hesse-darmstadt.friederike-luise")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["relationships"]["titles"]["data"] == []


def test_get_person_not_found(client):
    response = client.get("/people/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_include_titles_returns_bare_resource(client):
    response = client.get("/people/hesse-darmstadt.ludwig-ix?include=titles")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 1
    assert included[0]["type"] == "titles"
    assert included[0]["id"] == "hesse-darmstadt.landgrave"
    assert included[0].get("relationships") is None


def test_include_titles_absent_when_no_titles(client):
    response = client.get("/people/hesse-darmstadt.friederike-luise?include=titles")
    assert response.status_code == 200
    assert response.json().get("included") is None


def test_include_unrecognized_type_is_inert(client):
    response = client.get("/people?include=bogus")
    assert response.status_code == 200
    assert response.json().get("included") is None


def test_get_person_families_as_father(client):
    response = client.get("/people/hesse-darmstadt.ludwig-ix")
    body = response.json()["data"]
    assert body["relationships"]["families"]["data"] == [
        {"type": "families", "id": FAMILY_SLUG}
    ]


def test_get_person_families_as_child(client):
    response = client.get("/people/hesse-darmstadt.ludwig-i")
    body = response.json()["data"]
    assert body["relationships"]["families"]["data"] == [
        {"type": "families", "id": FAMILY_SLUG}
    ]


def test_include_families_returns_bare_resource(client):
    response = client.get("/people/hesse-darmstadt.friederike-luise?include=families")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 1
    assert included[0]["type"] == "families"
    assert included[0]["id"] == FAMILY_SLUG
    assert included[0].get("relationships") is None


def test_links_self(client):
    response = client.get("/people/hesse-darmstadt.ludwig-ix")
    self_link = response.json()["data"]["links"]["self"]
    assert self_link.endswith("/people/hesse-darmstadt.ludwig-ix")
