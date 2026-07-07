from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.models.user import User
from app.schemas.order import OrderConfirmIn, OrderCreateIn, OrderDetailOut, OrderListOut, OrderShipIn
from app.services.order_service import OrderService

router = APIRouter()


def _order_list_item(order) -> dict:
    return OrderListOut.model_validate(order).model_copy(update={"item_count": len(order.items)}).model_dump()


@router.post("/confirm")
def confirm_order(
    payload: OrderConfirmIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = OrderService(db).confirm_order(current_user.id, payload)
    return success(result.model_dump())


@router.post("")
def create_order(
    payload: OrderCreateIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OrderService(db).create_order(current_user.id, payload, idempotency_key)
    return success(OrderDetailOut.model_validate(order).model_dump())


@router.get("")
def list_orders(
    status: str | None = Query(default=None, max_length=32),
    page: PageParams = Depends(get_page_params),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = OrderService(db).list_orders(current_user.id, page, status)
    return page_response([_order_list_item(item) for item in items], page.page, page.page_size, total)


@router.get("/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).get_order(current_user.id, order_id)
    return success(OrderDetailOut.model_validate(order).model_dump())


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).cancel_order(current_user.id, order_id)
    return success(OrderDetailOut.model_validate(order).model_dump())


@router.post("/{order_id}/ship")
def ship_order(
    order_id: int,
    payload: OrderShipIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = OrderService(db).ship_order(current_user.id, order_id, payload)
    return success(OrderDetailOut.model_validate(order).model_dump())


@router.post("/{order_id}/receive")
def receive_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).receive_order(current_user.id, order_id)
    return success(OrderDetailOut.model_validate(order).model_dump())


@router.post("/{order_id}/complete")
def complete_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = OrderService(db).complete_order(current_user.id, order_id)
    return success(OrderDetailOut.model_validate(order).model_dump())
