from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.response import success
from app.models.user import User
from app.schemas.payment import PaymentCreateIn, PaymentCreateOut, PaymentOut
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("")
def create_payment(
    payload: PaymentCreateIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PaymentService(db)
    payment = service.create_payment(current_user.id, payload, idempotency_key)
    return success(
        PaymentCreateOut.model_validate(payment).model_copy(update={"pay_url": service.build_pay_url(payment)}).model_dump()
    )


@router.get("/{payment_id}")
def get_payment(payment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payment = PaymentService(db).get_payment(current_user.id, payment_id)
    return success(PaymentOut.model_validate(payment).model_dump())


@router.post("/{payment_id}/mock-success")
def mock_success(payment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payment = PaymentService(db).mock_success(current_user.id, payment_id)
    return success(PaymentOut.model_validate(payment).model_dump())


@router.post("/alipay/notify")
async def alipay_notify(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    form_data = {key: str(value) for key, value in form.items()}
    PaymentService(db).handle_alipay_notify(form_data)
    return PlainTextResponse("success")


@router.get("/alipay/return")
def alipay_return():
    return success({"message": "alipay sandbox return received"})
