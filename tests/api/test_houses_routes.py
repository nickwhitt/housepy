def test_list_houses(client, make_house):
    make_house(slug="test.house-a")
    make_house(slug="test.house-b")

    response = client.get("/v1/houses")
    assert response.status_code == 200
    data = response.json()["data"]
    assert {item["id"] for item in data} == {"test.house-a", "test.house-b"}
    assert all(item["type"] == "houses" for item in data)


def test_list_houses_paginates(client, make_house):
    for i in range(3):
        make_house(slug=f"test.house-{i}")

    response = client.get("/v1/houses?page[size]=2")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 2
    assert body["links"]["next"] is not None
    assert body["links"]["prev"] is None


def test_get_house_with_parent_and_founder(client, make_house, make_person, make_event):
    parent = make_house(slug="test.parent-house")
    founder = make_person(slug="test.founder")
    founded = make_event(year=1740)
    house = make_house(
        slug="test.house", parent=parent, founder=founder, founded=founded
    )
    member = make_person(slug="test.member", house=house)

    response = client.get(f"/v1/houses/{house.slug}")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["attributes"]["founded"]["year"] == 1740
    assert body["relationships"]["parent"]["data"] == {
        "type": "houses",
        "id": "test.parent-house",
    }
    assert body["relationships"]["founder"]["data"] == {
        "type": "people",
        "id": "test.founder",
    }
    ids = {item["id"] for item in body["relationships"]["members"]["data"]}
    assert ids == {member.slug}


def test_get_house_root_has_no_parent_but_has_cadet_branch(client, make_house):
    root = make_house(slug="test.root")
    make_house(slug="test.cadet", parent=root)

    response = client.get(f"/v1/houses/{root.slug}")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["relationships"]["parent"]["data"] is None
    assert body["relationships"]["cadet_branches"]["data"] == [
        {"type": "houses", "id": "test.cadet"}
    ]


def test_get_house_renamed_from(client, make_house):
    predecessor = make_house(slug="test.battenberg")
    house = make_house(slug="test.mountbatten", renamed_from=predecessor)

    response = client.get(f"/v1/houses/{house.slug}")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["relationships"]["renamed_from"]["data"] == {
        "type": "houses",
        "id": "test.battenberg",
    }


def test_get_house_renamed_from_null_when_unset(client, make_house):
    house = make_house(slug="test.house")

    response = client.get(f"/v1/houses/{house.slug}")
    body = response.json()["data"]
    assert body["relationships"]["renamed_from"]["data"] is None


def test_get_house_not_found(client):
    response = client.get("/v1/houses/does-not-exist")
    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"status": "404", "title": "Not Found", "detail": "not found"}
    ]


def test_include_houses_returns_bare_parent(client, make_house):
    parent = make_house(slug="test.parent-house")
    house = make_house(slug="test.house", parent=parent)

    response = client.get(f"/v1/houses/{house.slug}?include=houses")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 1
    assert included[0]["type"] == "houses"
    assert included[0]["id"] == "test.parent-house"
    assert included[0].get("relationships") is None


def test_links_self(client, make_house):
    house = make_house(slug="test.house")

    response = client.get(f"/v1/houses/{house.slug}")
    self_link = response.json()["data"]["links"]["self"]
    assert self_link.endswith(f"/v1/houses/{house.slug}")
