def test_list_houses(client):
    response = client.get("/houses")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert all(item["type"] == "houses" for item in data)


def test_get_house_with_parent_and_founder(client):
    response = client.get("/houses/hesse-darmstadt")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["attributes"]["founded"]["year"] == 1740
    assert body["relationships"]["parent"]["data"] == {
        "type": "houses",
        "id": "hesse",
    }
    assert body["relationships"]["founder"]["data"] == {
        "type": "people",
        "id": "hesse-darmstadt.ludwig-ix",
    }
    ids = {item["id"] for item in body["relationships"]["members"]["data"]}
    assert ids == {
        "hesse-darmstadt.ludwig-ix",
        "hesse-darmstadt.friederike-luise",
        "hesse-darmstadt.ludwig-i",
    }


def test_get_house_root_has_no_parent_but_has_cadet_branch(client):
    response = client.get("/houses/hesse")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["relationships"]["parent"]["data"] is None
    assert body["relationships"]["cadet_branches"]["data"] == [
        {"type": "houses", "id": "hesse-darmstadt"}
    ]


def test_get_house_not_found(client):
    response = client.get("/houses/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_include_houses_returns_bare_parent(client):
    response = client.get("/houses/hesse-darmstadt?include=houses")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 1
    assert included[0]["type"] == "houses"
    assert included[0]["id"] == "hesse"
    assert included[0].get("relationships") is None


def test_links_self(client):
    response = client.get("/houses/hesse-darmstadt")
    self_link = response.json()["data"]["links"]["self"]
    assert self_link.endswith("/houses/hesse-darmstadt")
