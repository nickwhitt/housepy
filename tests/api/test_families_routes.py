FAMILY_SLUG = "hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1"


def test_list_families(client):
    response = client.get("/families")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["type"] == "families"


def test_get_family(client):
    response = client.get(f"/families/{FAMILY_SLUG}")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["attributes"]["married"]["year"] == 1741
    assert body["relationships"]["father"]["data"] == {
        "type": "people",
        "id": "hesse-darmstadt.ludwig-ix",
    }
    assert body["relationships"]["mother"]["data"] == {
        "type": "people",
        "id": "hesse-darmstadt.friederike-luise",
    }
    assert body["relationships"]["children"]["data"] == [
        {"type": "people", "id": "hesse-darmstadt.ludwig-i"}
    ]


def test_get_family_not_found(client):
    response = client.get("/families/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_include_people_returns_bare_resources(client):
    response = client.get(f"/families/{FAMILY_SLUG}?include=people")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 3
    ids = {item["id"] for item in included}
    assert ids == {
        "hesse-darmstadt.ludwig-ix",
        "hesse-darmstadt.friederike-luise",
        "hesse-darmstadt.ludwig-i",
    }
    assert all(item["type"] == "people" for item in included)
    assert all(item.get("relationships") is None for item in included)


def test_links_self(client):
    response = client.get(f"/families/{FAMILY_SLUG}")
    self_link = response.json()["data"]["links"]["self"]
    assert self_link.endswith(f"/families/{FAMILY_SLUG}")
