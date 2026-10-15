"""A tiny orders API used to demonstrate the delivery platform.

It is deliberately small: the interesting part of this repo is not the app,
it is everything around the app (CI, Helm, GitOps, monitoring).
"""
import random
import time
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="orders-api", version="0.1.0")

# In-memory store. A real service would use a database; for a platform demo
# this keeps the focus on delivery instead of data plumbing.
_orders: Dict[int, dict] = {}


class OrderCreate(BaseModel):
    item: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)


class Order(OrderCreate):
    id: int
    total: float
    status: str
    created_at: float


def _next_id() -> int:
    # NOTE: random IDs can collide, which once made a test flaky (see issue).
    # Kept simple here on purpose; the fix is tracked in the repo history.
    return random.randint(1, 100)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/orders", status_code=201)
def create_order(payload: OrderCreate) -> dict:
    order_id = _next_id()
    order = Order(
        id=order_id,
        total=round(payload.quantity * payload.price, 2),
        status="created",
        created_at=time.time(),
        **payload.model_dump(),
    )
    _orders[order_id] = order.model_dump()
    return _orders[order_id]


@app.get("/orders")
def list_orders() -> List[dict]:
    return list(_orders.values())


@app.get("/orders/{order_id}")
def get_order(order_id: int) -> dict:
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order


@app.patch("/orders/{order_id}/cancel")
def cancel_order(order_id: int) -> dict:
    order = _orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    if order["status"] == "cancelled":
        raise HTTPException(status_code=409, detail="order already cancelled")
    order["status"] = "cancelled"
    return order


def reset_store() -> None:
    """Test helper: clears the in-memory store between tests."""
    _orders.clear()
