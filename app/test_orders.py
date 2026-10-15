"""Tests for the orders API."""
from fastapi.testclient import TestClient

from app.orders import app, reset_store

client = TestClient(app)


def setup_function():
    reset_store()


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_order_returns_total():
    resp = client.post(
        "/orders", json={"item": "laptop", "quantity": 2, "price": 999.99}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["item"] == "laptop"
    assert body["total"] == 1999.98
    assert body["status"] == "created"


def test_create_order_rejects_bad_input():
    resp = client.post("/orders", json={"item": "", "quantity": 0, "price": -5})
    assert resp.status_code == 422


def test_two_orders_get_different_ids():
    first = client.post(
        "/orders", json={"item": "mouse", "quantity": 1, "price": 25.0}
    ).json()
    second = client.post(
        "/orders", json={"item": "keyboard", "quantity": 1, "price": 75.0}
    ).json()
    assert first["id"] != second["id"]


def test_get_missing_order_returns_404():
    resp = client.get("/orders/does-not-exist")
    assert resp.status_code == 404


def test_cancel_order():
    created = client.post(
        "/orders", json={"item": "monitor", "quantity": 1, "price": 199.0}
    ).json()
    resp = client.patch(f"/orders/{created['id']}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


def test_cancel_twice_returns_409():
    created = client.post(
        "/orders", json={"item": "cable", "quantity": 3, "price": 9.99}
    ).json()
    client.patch(f"/orders/{created['id']}/cancel")
    resp = client.patch(f"/orders/{created['id']}/cancel")
    assert resp.status_code == 409


def test_list_orders():
    client.post("/orders", json={"item": "a", "quantity": 1, "price": 1.0})
    client.post("/orders", json={"item": "b", "quantity": 1, "price": 2.0})
    resp = client.get("/orders")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
