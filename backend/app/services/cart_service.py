from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.models.cart import CartItem
from app.models.product import ProductSku
from app.repositories.cart_repo import CartRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.cart import CartItemAddIn, CartItemOut, CartItemUpdateIn, CartOut, CartSelectIn


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CartRepository(db)
        self.product_repo = ProductRepository(db)

    def list_cart(self, user_id: int) -> CartOut:
        items = [self._to_item_out(item) for item in self.repo.list_user_items(user_id)]
        return CartOut(
            items=items,
            total_quantity=sum(item.quantity for item in items),
            selected_quantity=sum(item.quantity for item in items if item.selected and item.valid),
            selected_total_cent=sum(item.line_total_cent for item in items if item.selected and item.valid),
        )

    def add_item(self, user_id: int, payload: CartItemAddIn) -> CartItem:
        sku = self._get_available_sku(payload.sku_id, payload.quantity)
        item = self.repo.get_user_item_by_sku(user_id, payload.sku_id)
        if item:
            item.product_id = sku.product_id
            item.quantity = item.quantity + payload.quantity
            item.selected = payload.selected
            item.status = "active"
            item.deleted_at = None
            self._ensure_stock(sku, item.quantity)
            return self.repo.save(item)
        item = CartItem(
            user_id=user_id,
            product_id=sku.product_id,
            sku_id=sku.id,
            quantity=payload.quantity,
            selected=payload.selected,
        )
        return self.repo.save(item)

    def update_item(self, user_id: int, item_id: int, payload: CartItemUpdateIn) -> CartItem:
        item = self._get_user_item(user_id, item_id)
        data = payload.model_dump(exclude_unset=True)
        if "quantity" in data and data["quantity"] is not None:
            self._ensure_stock(item.sku, data["quantity"])
        for field, value in data.items():
            setattr(item, field, value)
        return self.repo.save(item)

    def select_items(self, user_id: int, payload: CartSelectIn) -> list[CartItem]:
        items = self.repo.list_user_items(user_id)
        target_ids = set(payload.item_ids or [item.id for item in items])
        selected_items = [item for item in items if item.id in target_ids]
        for item in selected_items:
            item.selected = payload.selected
        return self.repo.save_many(selected_items)

    def delete_item(self, user_id: int, item_id: int) -> None:
        item = self._get_user_item(user_id, item_id)
        item.status = "deleted"
        item.deleted_at = datetime.now(timezone.utc)
        self.repo.save(item)

    def clear_cart(self, user_id: int, selected_only: bool = False) -> int:
        items = self.repo.list_user_items(user_id)
        if selected_only:
            items = [item for item in items if item.selected]
        now = datetime.now(timezone.utc)
        for item in items:
            item.status = "deleted"
            item.deleted_at = now
        self.repo.save_many(items)
        return len(items)

    def _get_user_item(self, user_id: int, item_id: int) -> CartItem:
        item = self.repo.get_user_item(user_id, item_id)
        if item is None:
            raise AppException(ErrorCode.not_found, "购物车商品不存在", 404)
        return item

    def _get_available_sku(self, sku_id: int, quantity: int) -> ProductSku:
        sku = self.product_repo.get_sku(sku_id)
        if sku is None or sku.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "SKU 不存在", 404)
        if sku.status != "active" or sku.product.status != "on_sale" or sku.product.deleted_at is not None:
            raise AppException(ErrorCode.validation_error, "商品不可购买", 400)
        self._ensure_stock(sku, quantity)
        return sku

    def _ensure_stock(self, sku: ProductSku, quantity: int) -> None:
        if sku.stock - sku.locked_stock < quantity:
            raise AppException(ErrorCode.validation_error, "SKU 库存不足", 400)

    def _to_item_out(self, item: CartItem) -> CartItemOut:
        available_stock = max(item.sku.stock - item.sku.locked_stock, 0)
        valid = (
            item.product.deleted_at is None
            and item.product.status == "on_sale"
            and item.sku.deleted_at is None
            and item.sku.status == "active"
            and available_stock >= item.quantity
        )
        invalid_reason = None
        if item.product.deleted_at is not None or item.product.status != "on_sale":
            invalid_reason = "商品已下架"
        elif item.sku.deleted_at is not None or item.sku.status != "active":
            invalid_reason = "SKU 已失效"
        elif available_stock < item.quantity:
            invalid_reason = "库存不足"
        return CartItemOut(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            sku_id=item.sku_id,
            quantity=item.quantity,
            selected=item.selected,
            status=item.status,
            created_at=item.created_at,
            updated_at=item.updated_at,
            product_title=item.product.title,
            product_main_image=item.product.main_image,
            sku_name=item.sku.sku_name,
            sku_specs=item.sku.specs,
            price_cent=item.sku.price_cent,
            stock=item.sku.stock,
            locked_stock=item.sku.locked_stock,
            available_stock=available_stock,
            line_total_cent=item.sku.price_cent * item.quantity,
            valid=valid,
            invalid_reason=invalid_reason,
        )
