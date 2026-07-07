from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.response import success
from app.models.user import User
from app.schemas.cart import CartItemAddIn, CartItemUpdateIn, CartSelectIn
from app.services.cart_service import CartService

router = APIRouter()


@router.get("")
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = CartService(db).list_cart(current_user.id)
    return success(cart.model_dump())


@router.post("/items")
def add_cart_item(
    payload: CartItemAddIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    CartService(db).add_item(current_user.id, payload)
    cart = CartService(db).list_cart(current_user.id)
    return success(cart.model_dump())


@router.patch("/items/{item_id}")
def update_cart_item(
    item_id: int,
    payload: CartItemUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    CartService(db).update_item(current_user.id, item_id, payload)
    cart = CartService(db).list_cart(current_user.id)
    return success(cart.model_dump())


@router.delete("/items/{item_id}")
def delete_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    CartService(db).delete_item(current_user.id, item_id)
    return success({"deleted": True})


@router.post("/select")
def select_cart_items(
    payload: CartSelectIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    CartService(db).select_items(current_user.id, payload)
    cart = CartService(db).list_cart(current_user.id)
    return success(cart.model_dump())


@router.delete("/clear")
def clear_cart(
    selected_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted_count = CartService(db).clear_cart(current_user.id, selected_only)
    return success({"deleted_count": deleted_count})
