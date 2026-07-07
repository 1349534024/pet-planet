from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.models.user import User
from app.schemas.merchant import (
    MerchantApplicationCreateIn,
    MerchantAuditDecisionIn,
    MerchantBackendDependencyOut,
    MerchantBackendPlaceholderOut,
    MerchantBusinessSummaryOut,
    MerchantCreateIn,
    MerchantOut,
    QualificationAuditDecisionIn,
    QualificationCreateIn,
    QualificationOut,
    StoreCreateIn,
    StoreOut,
)
from app.services.merchant_service import MERCHANT_REQUIRED_QUALIFICATIONS, MerchantService

router = APIRouter()


@router.get("")
def list_merchants(page: PageParams = Depends(get_page_params), db: Session = Depends(get_db)):
    items, total = MerchantService(db).list_public(page)
    return page_response([MerchantOut.model_validate(item).model_dump() for item in items], page.page, page.page_size, total)


@router.get("/application-requirements")
def get_application_requirements():
    return success(
        {
            merchant_type: sorted(required_types)
            for merchant_type, required_types in MERCHANT_REQUIRED_QUALIFICATIONS.items()
        }
    )


@router.post("")
def create_merchant(
    payload: MerchantCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    merchant = MerchantService(db).create(current_user.id, payload)
    return success(MerchantOut.model_validate(merchant).model_dump())


@router.post("/applications")
def submit_application(
    payload: MerchantApplicationCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    merchant = MerchantService(db).submit_application(current_user.id, payload)
    status = MerchantService(db).build_application_status(merchant)
    return success(status.model_dump())


@router.get("/applications/me")
def list_my_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = MerchantService(db)
    items = service.list_my_applications(current_user.id)
    return success([service.build_application_status(item).model_dump() for item in items])


@router.get("/applications/{merchant_id}")
def get_application_status(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    status = MerchantService(db).get_application_status(current_user.id, merchant_id)
    return success(status.model_dump())


@router.post("/applications/{merchant_id}/approve")
def approve_application(
    merchant_id: int,
    payload: MerchantAuditDecisionIn,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    status = MerchantService(db).approve_application(current_user.id, merchant_id, payload)
    return success(status.model_dump())


@router.post("/applications/{merchant_id}/reject")
def reject_application(
    merchant_id: int,
    payload: MerchantAuditDecisionIn,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    status = MerchantService(db).reject_application(current_user.id, merchant_id, payload)
    return success(status.model_dump())


@router.post("/qualifications/{qualification_id}/approve")
def approve_qualification(
    qualification_id: int,
    payload: QualificationAuditDecisionIn,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    item = MerchantService(db).approve_qualification(current_user.id, qualification_id, payload)
    return success(QualificationOut.model_validate(item).model_dump())


@router.post("/qualifications/{qualification_id}/reject")
def reject_qualification(
    qualification_id: int,
    payload: QualificationAuditDecisionIn,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    item = MerchantService(db).reject_qualification(current_user.id, qualification_id, payload)
    return success(QualificationOut.model_validate(item).model_dump())


@router.get("/me")
def list_my_merchants(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = MerchantService(db).list_mine(current_user.id)
    return success([MerchantOut.model_validate(item).model_dump() for item in items])


@router.get("/{merchant_id}/backend/dependencies")
def list_backend_dependencies(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = MerchantService(db).list_backend_dependencies(current_user.id, merchant_id)
    return success([MerchantBackendDependencyOut.model_validate(item).model_dump() for item in items])


@router.get("/{merchant_id}/backend/products")
def list_backend_products(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = MerchantService(db).build_backend_placeholder(current_user.id, merchant_id, "products")
    return success(MerchantBackendPlaceholderOut.model_validate(data).model_dump())


@router.get("/{merchant_id}/backend/orders")
def list_backend_orders(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = MerchantService(db).build_backend_placeholder(current_user.id, merchant_id, "orders")
    return success(MerchantBackendPlaceholderOut.model_validate(data).model_dump())


@router.get("/{merchant_id}/backend/after-sales")
def list_backend_after_sales(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = MerchantService(db).build_backend_placeholder(current_user.id, merchant_id, "after_sales")
    return success(MerchantBackendPlaceholderOut.model_validate(data).model_dump())


@router.get("/{merchant_id}/backend/reviews")
def list_backend_reviews(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = MerchantService(db).build_backend_placeholder(current_user.id, merchant_id, "reviews")
    return success(MerchantBackendPlaceholderOut.model_validate(data).model_dump())


@router.get("/{merchant_id}/backend/summary")
def get_backend_summary(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = MerchantService(db).build_business_summary(current_user.id, merchant_id)
    return success(MerchantBusinessSummaryOut.model_validate(data).model_dump())


@router.post("/{merchant_id}/qualifications")
def add_qualification(
    merchant_id: int,
    payload: QualificationCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = MerchantService(db).add_qualification(current_user.id, merchant_id, payload)
    return success(QualificationOut.model_validate(item).model_dump())


@router.get("/{merchant_id}/qualifications")
def list_qualifications(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = MerchantService(db).list_qualifications(current_user.id, merchant_id)
    return success([QualificationOut.model_validate(item).model_dump() for item in items])


@router.post("/{merchant_id}/stores")
def add_store(
    merchant_id: int,
    payload: StoreCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store = MerchantService(db).add_store(current_user.id, merchant_id, payload)
    return success(StoreOut.model_validate(store).model_dump())


@router.get("/{merchant_id}/stores")
def list_stores(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = MerchantService(db).list_stores(current_user.id, merchant_id)
    return success([StoreOut.model_validate(item).model_dump() for item in items])
