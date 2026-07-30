def test_list_titles(client):
    response = client.get("/titles")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert all(item["type"] == "titles" for item in data)


def test_get_title_with_multiple_holders(client):
    response = client.get("/titles/hesse-darmstadt.landgrave")
    assert response.status_code == 200
    holder_ids = {
        item["id"]
        for item in response.json()["data"]["relationships"]["holders"]["data"]
    }
    assert holder_ids == {"hesse-darmstadt.ludwig-ix", "hesse-darmstadt.ludwig-i"}


def test_get_title_with_single_holder(client):
    response = client.get("/titles/hesse-and-by-rhine.grand-duke")
    assert response.status_code == 200
    holder_ids = {
        item["id"]
        for item in response.json()["data"]["relationships"]["holders"]["data"]
    }
    assert holder_ids == {"hesse-darmstadt.ludwig-i"}


def test_get_title_not_found(client):
    response = client.get("/titles/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "not found"


def test_include_holders_returns_bare_resources(client):
    # `include` filters by resource type ("people"), not the relationship's
    # field name ("holders") — holders are ResourceIdentifiers of type "people".
    response = client.get("/titles/hesse-darmstadt.landgrave?include=people")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 2
    assert all(item["type"] == "people" for item in included)
    assert all(item.get("relationships") is None for item in included)


def test_include_holders_deduped_across_list(client):
    response = client.get("/titles?include=people")
    assert response.status_code == 200
    included = response.json()["included"]
    assert len(included) == 2
    ids = {item["id"] for item in included}
    assert ids == {"hesse-darmstadt.ludwig-ix", "hesse-darmstadt.ludwig-i"}
