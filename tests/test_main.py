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
        "people": "http://testserver/v1/people",
        "titles": "http://testserver/v1/titles",
        "families": "http://testserver/v1/families",
        "houses": "http://testserver/v1/houses",
    }


def test_responses_use_jsonapi_media_type(client):
    response = client.get("/v1/people")
    assert response.headers["content-type"] == "application/vnd.api+json"


def test_validation_error_uses_jsonapi_error_envelope(client):
    response = client.get("/v1/people?page[size]=not-a-number")
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/vnd.api+json"
    errors = response.json()["errors"]
    assert len(errors) == 1
    assert errors[0]["status"] == "422"
    assert errors[0]["title"] == "Unprocessable Content"
