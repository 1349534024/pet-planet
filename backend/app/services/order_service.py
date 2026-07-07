from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.cart import CartItem
from app.models.order import MallOrder, MallOrderItem
from app.models.product import InventoryLog, ProductSku
from app.repositories.cart_repo import CartRepository
from app.repositories.order_repo import OrderRepository
from app.schemas.order import OrderConfirmIn, OrderConfirmOut, OrderCreateIn, OrderItemConfirmOut, OrderShipIn


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)

    def confirm_order(self, user_id: int, payload: OrderConfirmIn) -> OrderConfirmOut:
        address = self._get_address(user_id, payload.address_id)
        cart_items = self._get_order_cart_items(user_id, payload.cart_item_ids)
        confirm_items = [self._to_confirm_item(item) for item in cart_items]
        total_amount = sum(item.total_amount_cent for item in confirm_items)
        return OrderConfirmOut(
            address_id=address.id,
            receiver_name=address.receiver_name,
            receiver_phone=address.receiver_phone,
            province=address.province,
            city=address.city,
            district=address.district,
            detail=address.detail,
            items=confirm_items,
            total_amount_cent=total_amount,
            freight_amount_cent=0,
            discount_amount_cent=0,
            pay_amount_cent=total_amount,
        )

    def create_order(self, user_id: int, payload: OrderCreateIn, idempotency_key: str | None = None) -> MallOrder:
        if idempotency_key:
            existing = self.repo.get_by_idempotency_key(user_id, idempotency_key)
            if existing:
                return existing
        address = self._get_address(user_id, payload.address_id)
        cart_items = self._get_order_cart_items(user_id, payload.cart_item_ids)
        order_no = self._generate_order_no()
        order = MallOrder(
            order_no=order_no,
            user_id=user_id,
            address_id=address.id,
            receiver_name=address.receiver_name,
            receiver_phone=address.receiver_phone,
            province=address.province,
            city=address.city,
            district=address.district,
            detail=address.detail,
            remark=payload.remark,
            idempotency_key=idempotency_key,
        )
        total_amount = 0
        now = datetime.now(timezone.utc)
        try:
            self.db.add(order)
            self.db.flush()
            for cart_item in cart_items:
                sku = self._lock_and_get_sku(cart_item.sku_id, cart_item.quantity, order_no)
                line_total = sku.price_cent * cart_item.quantity
                total_amount += line_total
                order.items.append(
                    MallOrderItem(
                        order_id=order.id,
                        order_no=order_no,
                        product_id=cart_item.product_id,
                        sku_id=cart_item.sku_id,
                        merchant_id=cart_item.product.merchant_id,
                        product_title=cart_item.product.title,
                        product_main_image=cart_item.product.main_image,
                        sku_name=sku.sku_name,
                        sku_specs=sku.specs,
                        unit_price_cent=sku.price_cent,
                        quantity=cart_item.quantity,
                        total_amount_cent=line_total,
                    )
                )
                cart_item.status = "ordered"
                cart_item.deleted_at = now
            order.total_amount_cent = total_amount
            order.freight_amount_cent = 0
            order.discount_amount_cent = 0
            order.pay_amount_cent = total_amount
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "订单创建冲突，请重试", 409) from exc
        except Exception:
            self.db.rollback()
            raise
        return self.get_order(user_id, order.id)

    def list_orders(self, user_id: int, page: PageParams, status: str | None = None) -> tuple[list[MallOrder], int]:
        return self.repo.list_user_orders(user_id, page, status)

    def get_order(self, user_id: int, order_id: int) -> MallOrder:
        order = self.repo.get_by_id(user_id, order_id)
        if order is None:
            raise AppException(ErrorCode.order_not_found, "订单不存在", 404)
        return order

    def cancel_order(self, user_id: int, order_id: int) -> MallOrder:
        order = self.get_order(user_id, order_id)
        if order.status != "pending_payment":
            raise AppException(ErrorCode.order_status_invalid, "当前订单状态不可取消", 400)
        try:
            for item in order.items:
                sku = self.repo.get_sku_for_update(item.sku_id)
                if sku is None:
                    continue
                locked_before = sku.locked_stock
                sku.locked_stock = max(sku.locked_stock - item.quantity, 0)
                self.db.add(
                    InventoryLog(
                        product_id=item.product_id,
                        sku_id=item.sku_id,
                        change_type="unlock",
                        change_quantity=-item.quantity,
                        stock_before=locked_before,
                        stock_after=sku.locked_stock,
                        related_type="order",
                        related_id=order.order_no,
                        remark="取消订单释放锁定库存",
                    )
                )
            order.status = "canceled"
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
        except Exception:
            self.db.rollback()
            raise
        return self.get_order(user_id, order.id)

    def ship_order(self, user_id: int, order_id: int, payload: OrderShipIn) -> MallOrder:
        order = self.get_order(user_id, order_id)
        if order.status != "pending_shipment" or order.payment_status != "paid":
            raise AppException(ErrorCode.order_status_invalid, "当前订单状态不可发货", 400)
        order.status = "shipped"
        order.tracking_company = payload.tracking_company
        order.tracking_no = payload.tracking_no
        order.shipped_at = datetime.now(timezone.utc)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return self.get_order(user_id, order.id)

    def receive_order(self, user_id: int, order_id: int) -> MallOrder:
        order = self.get_order(user_id, order_id)
        if order.status != "shipped":
            raise AppException(ErrorCode.order_status_invalid, "当前订单状态不可确认收货", 400)
        order.status = "received"
        order.received_at = datetime.now(timezone.utc)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return self.get_order(user_id, order.id)

    def complete_order(self, user_id: int, order_id: int) -> MallOrder:
        order = self.get_order(user_id, order_id)
        if order.status not in {"received", "shipped"}:
            raise AppException(ErrorCode.order_status_invalid, "当前订单状态不可完成", 400)
        now = datetime.now(timezone.utc)
        order.status = "completed"
        if order.received_at is None:
            order.received_at = now
        order.completed_at = now
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return self.get_order(user_id, order.id)

    def _get_address(self, user_id: int, address_id: int):
        address = self.repo.get_address(user_id, address_id)
        if address is None:
            raise AppException(ErrorCode.not_found, "收货地址不存在", 404)
        return address

    def _get_order_cart_items(self, user_id: int, cart_item_ids: list[int] | None) -> list[CartItem]:
        cart_items = self.cart_repo.list_user_items(user_id)
        if cart_item_ids:
            target_ids = set(cart_item_ids)
            cart_items = [item for item in cart_items if item.id in target_ids]
            if {item.id for item in cart_items} != target_ids:
                raise AppException(ErrorCode.validation_error, "购物车商品不存在", 400)
        else:
            cart_items = [item for item in cart_items if item.selected]
        if not cart_items:
            raise AppException(ErrorCode.validation_error, "请选择要结算的商品", 400)
        for item in cart_items:
            self._validate_cart_item(item)
        return cart_items

    def _validate_cart_item(self, item: CartItem) -> None:
        available_stock = item.sku.stock - item.sku.locked_stock
        if item.product.deleted_at is not None or item.product.status != "on_sale":
            raise AppException(ErrorCode.validation_error, "商品已下架", 400)
        if item.sku.deleted_at is not None or item.sku.status != "active":
            raise AppException(ErrorCode.validation_error, "SKU 已失效", 400)
        if available_stock < item.quantity:
            raise AppException(ErrorCode.validation_error, "SKU 库存不足", 400)

    def _lock_and_get_sku(self, sku_id: int, quantity: int, order_no: str) -> ProductSku:
        sku = self.repo.get_sku_for_update(sku_id)
        if sku is None or sku.deleted_at is not None or sku.status != "active":
            raise AppException(ErrorCode.validation_error, "SKU 已失效", 400)
        if sku.product.deleted_at is not None or sku.product.status != "on_sale":
            raise AppException(ErrorCode.validation_error, "商品已下架", 400)
        available_stock = sku.stock - sku.locked_stock
        if available_stock < quantity:
            raise AppException(ErrorCode.validation_error, "SKU 库存不足", 400)
        locked_before = sku.locked_stock
        sku.locked_stock += quantity
        self.db.add(
            InventoryLog(
                product_id=sku.product_id,
                sku_id=sku.id,
                change_type="lock",
                change_quantity=quantity,
                stock_before=locked_before,
                stock_after=sku.locked_stock,
                related_type="order",
                related_id=order_no,
                remark="创建订单锁定库存",
            )
        )
        return sku

    def _to_confirm_item(self, item: CartItem) -> OrderItemConfirmOut:
        available_stock = max(item.sku.stock - item.sku.locked_stock, 0)
        return OrderItemConfirmOut(
            cart_item_id=item.id,
            product_id=item.product_id,
            sku_id=item.sku_id,
            product_title=item.product.title,
            product_main_image=item.product.main_image,
            sku_name=item.sku.sku_name,
            sku_specs=item.sku.specs,
            unit_price_cent=item.sku.price_cent,
            quantity=item.quantity,
            total_amount_cent=item.sku.price_cent * item.quantity,
            available_stock=available_stock,
        )

    def _generate_order_no(self) -> str:
        return f"MO{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{uuid4().hex[:10].upper()}"
