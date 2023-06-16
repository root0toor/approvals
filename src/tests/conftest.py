import pytest
from main import app
from fastapi.testclient import TestClient

@pytest.fixture()
def client():
    with TestClient(app=app) as c:
        yield c
