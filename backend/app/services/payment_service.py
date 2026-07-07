from datetime import datetime, timezone
import base64
import json
from decimal import Decimal
from urllib.parse import urlencode
from uuid import uuid4

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppException, ErrorCode
from app.models.payment import PaymentOrder
from app.models.product import InventoryLog
from app.repositories.payment_repo import PaymentRepository
from app.schemas.payment import PaymentCreateIn


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PaymentRepository(db)

    def create_payment(
        self,
        user_id: int,
        payload: PaymentCreateIn,
        idempotency_key: str | None = None,
    ) -> PaymentOrder:
        if payload.pay_channel not in {"mock", "alipay_sandbox"}:
            raise AppException(ErrorCode.validation_error, "不支持的支付渠道", 400)
        if payload.pay_channel == "alipay_sandbox":
            self._ensure_alipay_configured()
        if idempotency_key:
            existing = self.repo.get_by_idempotency_key(user_id, idempotency_key)
            if existing:
                return existing
        order = self.repo.get_order_for_update(user_id, payload.order_id)
        if order is None:
            raise AppException(ErrorCode.order_not_found, "订单不存在", 404)
        if order.status != "pending_payment" or order.payment_status != "unpaid":
            raise AppException(ErrorCode.order_status_invalid, "当前订单状态不可支付", 400)
        active_payment = self.repo.get_active_by_order_id(user_id, payload.order_id)
        if active_payment:
            return active_payment
        payment = PaymentOrder(
            payment_no=self._generate_payment_no(),
            order_id=order.id,
            order_no=order.order_no,
            user_id=user_id,
            pay_amount_cent=order.pay_amount_cent,
            pay_channel=payload.pay_channel,
            idempotency_key=idempotency_key,
        )
        try:
            return self.repo.save(payment)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "支付单创建冲突，请重试", 409) from exc

    def get_payment(self, user_id: int, payment_id: int) -> PaymentOrder:
        payment = self.repo.get_payment(user_id, payment_id)
        if payment is None:
            raise AppException(ErrorCode.not_found, "支付单不存在", 404)
        return payment

    def build_pay_url(self, payment: PaymentOrder) -> str | None:
        if payment.pay_channel != "alipay_sandbox" or payment.status != "pending":
            return None
        self._ensure_alipay_configured()
        params = {
            "app_id": settings.alipay_sandbox_app_id,
            "method": "alipay.trade.page.pay",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": settings.alipay_sandbox_notify_url,
            "return_url": settings.alipay_sandbox_return_url,
            "biz_content": json.dumps(
                {
                    "out_trade_no": payment.payment_no,
                    "total_amount": self._cent_to_yuan(payment.pay_amount_cent),
                    "subject": f"宠物星球订单 {payment.order_no}",
                    "product_code": "FAST_INSTANT_TRADE_PAY",
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        }
        params["sign"] = self._alipay_sign(params)
        return f"{settings.alipay_sandbox_gateway}?{urlencode(params)}"

    def mock_success(self, user_id: int, payment_id: int) -> PaymentOrder:
        payment = self.repo.get_payment_for_update(user_id, payment_id)
        if payment is None:
            raise AppException(ErrorCode.not_found, "支付单不存在", 404)
        return self._mark_payment_paid(payment, f"MOCK{uuid4().hex[:18].upper()}")

    def handle_alipay_notify(self, form_data: dict[str, str]) -> bool:
        if not self.verify_alipay_notify(form_data):
            raise AppException(ErrorCode.payment_callback_invalid, "支付宝回调验签失败", 400)
        trade_status = form_data.get("trade_status")
        if trade_status not in {"TRADE_SUCCESS", "TRADE_FINISHED"}:
            return True
        payment_no = form_data.get("out_trade_no")
        if not payment_no:
            raise AppException(ErrorCode.payment_callback_invalid, "支付宝回调缺少商户订单号", 400)
        payment = self.repo.get_by_payment_no_for_update(payment_no)
        if payment is None:
            raise AppException(ErrorCode.not_found, "支付单不存在", 404)
        if payment.pay_channel != "alipay_sandbox":
            raise AppException(ErrorCode.payment_callback_invalid, "支付渠道不匹配", 400)
        total_amount = form_data.get("total_amount")
        if total_amount and total_amount != self._cent_to_yuan(payment.pay_amount_cent):
            raise AppException(ErrorCode.payment_callback_invalid, "支付金额不匹配", 400)
        self._mark_payment_paid(payment, form_data.get("trade_no"))
        return True

    def verify_alipay_notify(self, form_data: dict[str, str]) -> bool:
        self._ensure_alipay_configured()
        sign = form_data.get("sign")
        if not sign:
            return False
        sign_content = self._alipay_sign_content(form_data)
        public_key = serialization.load_pem_public_key(self._format_public_key(settings.alipay_sandbox_public_key))
        try:
            public_key.verify(base64.b64decode(sign), sign_content.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
        except (InvalidSignature, ValueError):
            return False
        return True

    def _mark_payment_paid(self, payment: PaymentOrder, trade_no: str | None) -> PaymentOrder:
        if payment.status == "paid":
            return payment
        if payment.status != "pending":
            raise AppException(ErrorCode.validation_error, "当前支付单状态不可支付成功", 400)
        order = self.repo.get_order_for_update(payment.user_id, payment.order_id)
        if order is None:
            raise AppException(ErrorCode.order_not_found, "订单不存在", 404)
        if order.status != "pending_payment" or order.payment_status != "unpaid":
            raise AppException(ErrorCode.order_status_invalid, "当前订单状态不可支付成功", 400)
        try:
            for item in order.items:
                sku = self.repo.get_sku_for_update(item.sku_id)
                if sku is None:
                    raise AppException(ErrorCode.validation_error, "SKU 已失效", 400)
                if sku.stock < item.quantity or sku.locked_stock < item.quantity:
                    raise AppException(ErrorCode.validation_error, "SKU 库存不足", 400)
                stock_before = sku.stock
                sku.stock -= item.quantity
                sku.locked_stock = max(sku.locked_stock - item.quantity, 0)
                self.db.add(
                    InventoryLog(
                        product_id=item.product_id,
                        sku_id=item.sku_id,
                        change_type="pay_deduct",
                        change_quantity=-item.quantity,
                        stock_before=stock_before,
                        stock_after=sku.stock,
                        related_type="payment",
                        related_id=payment.payment_no,
                        remark="支付成功扣减库存",
                    )
                )
            payment.status = "paid"
            payment.paid_at = datetime.now(timezone.utc)
            payment.third_party_trade_no = trade_no
            order.status = "pending_shipment"
            order.payment_status = "paid"
            self.db.add(payment)
            self.db.add(order)
            self.db.commit()
            self.db.refresh(payment)
        except Exception:
            self.db.rollback()
            raise
        return payment

    def _generate_payment_no(self) -> str:
        return f"PAY{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{uuid4().hex[:10].upper()}"

    def _ensure_alipay_configured(self) -> None:
        if not (
            settings.alipay_sandbox_app_id
            and settings.alipay_sandbox_private_key
            and settings.alipay_sandbox_public_key
            and settings.alipay_sandbox_notify_url
            and settings.alipay_sandbox_return_url
        ):
            raise AppException(ErrorCode.validation_error, "支付宝沙箱配置不完整", 400)

    def _alipay_sign(self, params: dict[str, str | None]) -> str:
        private_key = self._load_private_key(settings.alipay_sandbox_private_key)
        signature = private_key.sign(
            self._alipay_sign_content(params).encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _alipay_sign_content(self, params: dict[str, str | None]) -> str:
        items = []
        for key in sorted(params):
            value = params[key]
            if key in {"sign", "sign_type"} or value is None or value == "":
                continue
            items.append(f"{key}={value}")
        return "&".join(items)

    def _format_private_key(self, key: str | None) -> bytes:
        if not key:
            raise AppException(ErrorCode.validation_error, "支付宝应用私钥未配置", 400)
        key = key.replace("\\n", "\n").strip()
        if "BEGIN" not in key:
            key = f"-----BEGIN PRIVATE KEY-----\n{key}\n-----END PRIVATE KEY-----"
        return key.encode("utf-8")

    def _load_private_key(self, key: str | None):
        if not key:
            raise AppException(ErrorCode.validation_error, "支付宝应用私钥未配置", 400)
        raw_key = key.replace("\\n", "\n").strip()
        candidates = [raw_key]
        if "BEGIN" not in raw_key:
            candidates = [
                f"-----BEGIN PRIVATE KEY-----\n{raw_key}\n-----END PRIVATE KEY-----",
                f"-----BEGIN RSA PRIVATE KEY-----\n{raw_key}\n-----END RSA PRIVATE KEY-----",
            ]
        last_error: Exception | None = None
        for candidate in candidates:
            try:
                return serialization.load_pem_private_key(candidate.encode("utf-8"), password=None)
            except ValueError as exc:
                last_error = exc
        raise AppException(ErrorCode.validation_error, "支付宝应用私钥格式无效", 400) from last_error

    def _format_public_key(self, key: str | None) -> bytes:
        if not key:
            raise AppException(ErrorCode.validation_error, "支付宝公钥未配置", 400)
        key = key.replace("\\n", "\n").strip()
        if "BEGIN" not in key:
            key = f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"
        return key.encode("utf-8")

    def _cent_to_yuan(self, amount_cent: int) -> str:
        return str((Decimal(amount_cent) / Decimal(100)).quantize(Decimal("0.01")))
