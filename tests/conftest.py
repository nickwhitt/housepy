import pytest
from fastapi.testclient import TestClient

from housepy.main import app


@pytest.fixture
def client():
    return TestClient(app)
