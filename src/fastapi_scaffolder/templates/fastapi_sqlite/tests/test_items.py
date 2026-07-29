import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    # Using a context manager triggers lifespan startup/shutdown,
    # which is what creates the SQLite tables.
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_item_crud_flow(client):
    # create
    resp = client.post("/api/v1/items/", json={"name": "Widget", "description": "A test widget"})
    assert resp.status_code == 201
    item = resp.json()
    item_id = item["id"]
    assert item["name"] == "Widget"

    # read one
    resp = client.get(f"/api/v1/items/{item_id}")
    assert resp.status_code == 200

    # list
    resp = client.get("/api/v1/items/")
    assert resp.status_code == 200
    assert any(i["id"] == item_id for i in resp.json())

    # update
    resp = client.patch(f"/api/v1/items/{item_id}", json={"description": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated"

    # delete
    resp = client.delete(f"/api/v1/items/{item_id}")
    assert resp.status_code == 204

    # confirm gone
    resp = client.get(f"/api/v1/items/{item_id}")
    assert resp.status_code == 404
