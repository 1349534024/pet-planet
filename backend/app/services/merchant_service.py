from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.merchant import Merchant, MerchantQualification, MerchantStore
from app.models.user import Role, User
from app.repositories.merchant_repo import MerchantRepository
from app.schemas.merchant import (
    MerchantApplicationCreateIn,
    MerchantApplicationStatusOut,
    MerchantBackendDependencyOut,
    MerchantBackendPlaceholderOut,
    MerchantBusinessSummaryOut,
    MerchantAuditDecisionIn,
    MerchantCreateIn,
    MerchantOut,
    QualificationAuditDecisionIn,
    QualificationCreateIn,
    StoreCreateIn,
)


MERCHANT_REQUIRED_QUALIFICATIONS: dict[str, set[str]] = {
    "pet_supplies": {"business_license", "legal_person_id_card"},
    "pet_shop": {"business_license", "legal_person_id_card", "store_photo"},
    "cattery": {"business_license", "legal_person_id_card", "breeding_license"},
    "kennel": {"business_license", "legal_person_id_card", "breeding_license"},
    "pet_grooming": {"business_license", "legal_person_id_card", "store_photo"},
    "pet_hospital": {"business_license", "legal_person_id_card", "medical_license"},
    "pet_boarding": {"business_license", "legal_person_id_card", "store_photo"},
    "rescue_org": {"organization_certificate", "responsible_person_id_card"},
    "individual_service": {"identity_card"},
}

MERCHANT_ROLE_BY_TYPE: dict[str, str] = {
    "pet_supplies": "merchant",
    "pet_shop": "merchant",
    "cattery": "merchant",
    "kennel": "merchant",
    "pet_grooming": "service_provider",
    "pet_hospital": "service_provider",
    "pet_boarding": "service_provider",
    "rescue_org": "rescue_org",
    "individual_service": "service_provider",
}

MERCHANT_BACKEND_DEPENDENCIES: dict[str, MerchantBackendDependencyOut] = {
    "products": MerchantBackendDependencyOut(
        module="products",
        dependency="product/product_sku/inventory models and merchant product APIs",
        note="商家商品管理复用 B 模块商品、SKU、库存能力；C 模块不新建商品表。",
    ),
    "orders": MerchantBackendDependencyOut(
        module="orders",
        dependency="order/order_item/payment_order models and merchant order APIs",
        note="商家订单处理复用 B 模块订单和支付状态机；C 模块只保留接口壳。",
    ),
    "after_sales": MerchantBackendDependencyOut(
        module="after_sales",
        dependency="after_sale/refund_order models and merchant after-sale APIs",
        note="售后审核复用 B 模块售后流程；C 模块不新建售后表。",
    ),
    "reviews": MerchantBackendDependencyOut(
        module="reviews",
        dependency="review model and merchant review APIs",
        note="评价管理复用 B 模块评价能力；C 模块不新建评价表。",
    ),
}


class MerchantService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MerchantRepository(db)

    def list_public(self, page: PageParams) -> tuple[list[Merchant], int]:
        return self.repo.list_approved(page)

    def list_mine(self, owner_id: int) -> list[Merchant]:
        return self.repo.list_by_owner(owner_id)

    def create(self, owner_id: int, payload: MerchantCreateIn) -> Merchant:
        merchant = Merchant(owner_id=owner_id, **payload.model_dump())
        return self.repo.create(merchant)

    def submit_application(self, owner_id: int, payload: MerchantApplicationCreateIn) -> Merchant:
        self._validate_application(payload)
        merchant_data = payload.model_dump(exclude={"qualifications", "stores"})
        merchant = Merchant(owner_id=owner_id, **merchant_data)
        merchant = self.repo.create(merchant)
        for qualification_payload in payload.qualifications:
            qualification = MerchantQualification(merchant_id=merchant.id, **qualification_payload.model_dump())
            self.repo.create(qualification)
        for store_payload in payload.stores:
            store = MerchantStore(merchant_id=merchant.id, **store_payload.model_dump())
            self.repo.create(store)
        return merchant

    def list_my_applications(self, owner_id: int) -> list[Merchant]:
        return self.repo.list_by_owner(owner_id)

    def get_application_status(self, owner_id: int, merchant_id: int) -> MerchantApplicationStatusOut:
        merchant = self.get_owned(owner_id, merchant_id)
        return self.build_application_status(merchant)

    def approve_application(
        self, auditor_id: int, merchant_id: int, payload: MerchantAuditDecisionIn
    ) -> MerchantApplicationStatusOut:
        merchant = self.get_application_for_audit(merchant_id)
        self._ensure_application_ready_for_approval(merchant)
        merchant.audit_status = "approved"
        merchant.audit_reason = payload.reason
        merchant.audited_by = auditor_id
        merchant.audited_at = datetime.now(timezone.utc)
        self._grant_owner_role(merchant)
        self.db.add(merchant)
        self.db.commit()
        self.db.refresh(merchant)
        return self.build_application_status(merchant)

    def reject_application(
        self, auditor_id: int, merchant_id: int, payload: MerchantAuditDecisionIn
    ) -> MerchantApplicationStatusOut:
        merchant = self.get_application_for_audit(merchant_id)
        merchant.audit_status = "rejected"
        merchant.audit_reason = payload.reason or "入驻申请未通过"
        merchant.audited_by = auditor_id
        merchant.audited_at = datetime.now(timezone.utc)
        self.db.add(merchant)
        self.db.commit()
        self.db.refresh(merchant)
        return self.build_application_status(merchant)

    def approve_qualification(
        self, auditor_id: int, qualification_id: int, payload: QualificationAuditDecisionIn
    ) -> MerchantQualification:
        qualification = self.get_qualification_for_audit(qualification_id)
        qualification.audit_status = "approved"
        qualification.audit_reason = payload.reason
        qualification.audited_by = auditor_id
        qualification.audited_at = datetime.now(timezone.utc)
        self.db.add(qualification)
        self.db.commit()
        self.db.refresh(qualification)
        return qualification

    def reject_qualification(
        self, auditor_id: int, qualification_id: int, payload: QualificationAuditDecisionIn
    ) -> MerchantQualification:
        qualification = self.get_qualification_for_audit(qualification_id)
        qualification.audit_status = "rejected"
        qualification.audit_reason = payload.reason or "资质审核未通过"
        qualification.audited_by = auditor_id
        qualification.audited_at = datetime.now(timezone.utc)
        merchant = self.repo.get(Merchant, qualification.merchant_id)
        if merchant is not None and merchant.audit_status == "approved":
            merchant.audit_status = "pending"
            merchant.audit_reason = "必要资质被驳回，需重新审核"
            self.db.add(merchant)
        self.db.add(qualification)
        self.db.commit()
        self.db.refresh(qualification)
        return qualification

    def get_qualification_for_audit(self, qualification_id: int) -> MerchantQualification:
        qualification = self.repo.get(MerchantQualification, qualification_id)
        if qualification is None or qualification.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "商家资质不存在", 404)
        return qualification

    def get_application_for_audit(self, merchant_id: int) -> Merchant:
        merchant = self.repo.get(Merchant, merchant_id)
        if merchant is None or merchant.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "入驻申请不存在", 404)
        return merchant

    def build_application_status(self, merchant: Merchant) -> MerchantApplicationStatusOut:
        required = sorted(MERCHANT_REQUIRED_QUALIFICATIONS.get(merchant.merchant_type, set()))
        qualifications = self.repo.list_qualifications(merchant.id)
        provided = {
            item.qualification_type
            for item in qualifications
            if item.deleted_at is None and item.audit_status != "rejected"
        }
        missing = [item for item in required if item not in provided]
        data = MerchantOut.model_validate(merchant).model_dump()
        data["required_qualification_types"] = required
        data["missing_qualification_types"] = missing
        data["can_publish_live_pet"] = merchant.audit_status == "approved" and merchant.merchant_type in {
            "pet_shop",
            "cattery",
            "kennel",
        }
        data["can_publish_service"] = merchant.audit_status == "approved" and merchant.merchant_type in {
            "pet_shop",
            "pet_grooming",
            "pet_hospital",
            "pet_boarding",
            "individual_service",
        }
        return MerchantApplicationStatusOut(**data)

    def get_owned(self, owner_id: int, merchant_id: int) -> Merchant:
        merchant = self.repo.get(Merchant, merchant_id)
        if merchant is None or merchant.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "商家不存在", 404)
        if merchant.owner_id != owner_id:
            raise AppException(ErrorCode.forbidden, "无权操作该商家", 403)
        return merchant

    def add_qualification(self, owner_id: int, merchant_id: int, payload: QualificationCreateIn) -> MerchantQualification:
        self.get_owned(owner_id, merchant_id)
        item = MerchantQualification(merchant_id=merchant_id, **payload.model_dump())
        return self.repo.create(item)

    def list_qualifications(self, owner_id: int, merchant_id: int) -> list[MerchantQualification]:
        self.get_owned(owner_id, merchant_id)
        return self.repo.list_qualifications(merchant_id)

    def add_store(self, owner_id: int, merchant_id: int, payload: StoreCreateIn) -> MerchantStore:
        self.get_owned(owner_id, merchant_id)
        store = MerchantStore(merchant_id=merchant_id, **payload.model_dump())
        return self.repo.create(store)

    def list_stores(self, owner_id: int, merchant_id: int) -> list[MerchantStore]:
        self.get_owned(owner_id, merchant_id)
        return self.repo.list_stores(merchant_id)

    def list_backend_dependencies(self, owner_id: int, merchant_id: int) -> list[MerchantBackendDependencyOut]:
        self.get_owned(owner_id, merchant_id)
        return list(MERCHANT_BACKEND_DEPENDENCIES.values())

    def build_backend_placeholder(
        self, owner_id: int, merchant_id: int, capability: str
    ) -> MerchantBackendPlaceholderOut:
        self.get_owned(owner_id, merchant_id)
        dependency = MERCHANT_BACKEND_DEPENDENCIES[capability]
        return MerchantBackendPlaceholderOut(
            merchant_id=merchant_id,
            capability=capability,
            dependencies=[dependency],
        )

    def build_business_summary(self, owner_id: int, merchant_id: int) -> MerchantBusinessSummaryOut:
        self.get_owned(owner_id, merchant_id)
        return MerchantBusinessSummaryOut(
            merchant_id=merchant_id,
            dependencies=[
                MERCHANT_BACKEND_DEPENDENCIES["orders"],
                MERCHANT_BACKEND_DEPENDENCIES["after_sales"],
                MERCHANT_BACKEND_DEPENDENCIES["reviews"],
            ],
        )

    def _validate_application(self, payload: MerchantApplicationCreateIn) -> None:
        if payload.merchant_type not in MERCHANT_REQUIRED_QUALIFICATIONS:
            raise AppException(ErrorCode.validation_error, "不支持的商家类型", 400)
        provided = {item.qualification_type for item in payload.qualifications}
        required = MERCHANT_REQUIRED_QUALIFICATIONS[payload.merchant_type]
        missing = sorted(required - provided)
        if missing:
            raise AppException(ErrorCode.validation_error, f"缺少必要资质: {', '.join(missing)}", 400)

    def _ensure_application_ready_for_approval(self, merchant: Merchant) -> None:
        required = MERCHANT_REQUIRED_QUALIFICATIONS.get(merchant.merchant_type, set())
        qualifications = self.repo.list_qualifications(merchant.id)
        approved_types = {
            item.qualification_type
            for item in qualifications
            if item.deleted_at is None and item.audit_status == "approved"
        }
        missing = sorted(required - approved_types)
        if missing:
            raise AppException(ErrorCode.validation_error, f"必要资质尚未审核通过: {', '.join(missing)}", 400)

    def _grant_owner_role(self, merchant: Merchant) -> None:
        role_code = MERCHANT_ROLE_BY_TYPE.get(merchant.merchant_type)
        if role_code is None:
            return
        owner = self.db.get(User, merchant.owner_id)
        role = self.db.scalar(select(Role).where(Role.code == role_code))
        if owner is None or role is None:
            return
        if all(existing.code != role_code for existing in owner.roles):
            owner.roles.append(role)
            self.db.add(owner)
