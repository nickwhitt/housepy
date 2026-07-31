def test_root_discovery_document(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["name"] == "HousePy API"
    assert body["meta"]["documentation"] == {
        "swagger": "http://testserver/docs",
        "redoc": "http://testserver/redoc",
        "openapi": "http://testserver/openapi.json",
    }
    assert body["links"] == {
        "people": "http://testserver/people",
        "titles": "http://testserver/titles",
        "families": "http://testserver/families",
        "houses": "http://testserver/houses",
    }
