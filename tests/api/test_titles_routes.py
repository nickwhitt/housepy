def test_list_titles(client, make_title):
    make_title(slug="test.duke")
    make_title(slug="test.duchess")

    response = client.get("/v1/titles")
    assert response.status_code == 200
    data = response.json()["data"]
    assert {item["id"] for item in data} == {"test.duke", "test.duchess"}
    assert all(item["type"] == "titles" for item in data)


def test_list_titles_paginates(client, make_title):
    for i in range(3):
        make_title(slug=f"test.title-{i}")

    response = client.get("/v1/titles?page[size]=2")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 2
    assert body["links"]["next"] is not None
    assert body["links"]["prev"] is None


def test_get_title_with_multiple_holders(client, make_person, make_title, make_tenure):
    title = make_title(slug="test.duke")
    alice = make_person(slug="test.alice")
    bob = make_person(slug="test.bob")
    make_tenure(person=alice, title=title)
    make_tenure(person=bob, title=title)

    response = client.get(f"/v1/titles/{title.slug}")
    assert response.status_code == 200
    holder_ids = {
        item["id"]
        for item in response.json()["data"]["relationships"]["holders"]["data"]
    }
    assert holder_ids == {"test.alice", "test.bob"}


def test_get_title_with_single_holder(client, make_person, make_title, make_tenure):
    title = make_title(slug="test.duke")
    alice = make_person(slug="test.alice")
    make_tenure(person=alice, title=title)

    response = client.get(f"/v1/titles/{title.slug}")
    assert response.status_code == 200
    holder_ids = {
        item["id"]
        for item in response.json()["data"]["relationships"]["holders"]["data"]
    }
    assert holder_ids == {"test.alice"}


def test_get_title_tenures_include_holder_and_dates(
    client, make_person, make_title, make_tenure, make_event
):
    title = make_title(slug="test.duke")
    alice = make_person(slug="test.alice")
    bob = make_person(slug="test.bob")
    make_tenure(person=alice, title=title, start=make_event(year=1768))
    make_tenure(
        person=bob, title=title, start=make_event(year=1790), end=make_event(year=1806)
    )

    response = client.get(f"/v1/titles/{title.slug}")
    assert response.status_code == 200
    tenures = response.json()["data"]["attributes"]["tenures"]
    by_person = {t["person"]: t for t in tenures}
    assert by_person["test.alice"]["start"]["year"] == 1768
    assert by_person["test.alice"]["end"] is None
    assert by_person["test.bob"]["start"]["year"] == 1790
    assert by_person["test.bob"]["end"]["year"] == 1806


def test_get_title_not_found(client):
    response = client.get("/v1/titles/does-not-exist")
    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"status": "404", "title": "Not Found", "detail": "not found"}
    ]


def test_include_holders_returns_bare_resources(
    client, make_person, make_title, make_tenure
):
    # `include` filters by resource type ("people"), not field name ("holders").
    title = make_title(slug="test.duke")
    alice = make_person(slug="test.alice")
    bob = make_person(slug="test.bob")
    make_tenure(person=alice, title=title)
    make_tenure(person=bob, title=title)

    response = client.get(f"/v1/titles/{title.slug}?include=people")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 2
    assert all(item["type"] == "people" for item in included)
    assert all(item.get("relationships") is None for item in included)


def test_include_holders_deduped_across_list(
    client, make_person, make_title, make_tenure
):
    duke = make_title(slug="test.duke")
    duchess = make_title(slug="test.duchess")
    alice = make_person(slug="test.alice")  # holds both titles
    make_tenure(person=alice, title=duke)
    make_tenure(person=alice, title=duchess)

    response = client.get("/v1/titles?include=people")
    assert response.status_code == 200
    included = response.json()["included"]
    ids = [item["id"] for item in included]
    assert len(ids) == len(set(ids))  # no repeats, regardless of dataset size
    assert ids.count("test.alice") == 1


def test_links_self(client, make_title):
    title = make_title(slug="test.duke")

    response = client.get(f"/v1/titles/{title.slug}")
    self_link = response.json()["data"]["links"]["self"]
    assert self_link.endswith(f"/v1/titles/{title.slug}")
