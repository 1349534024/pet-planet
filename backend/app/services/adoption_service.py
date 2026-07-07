from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.adoption import AdoptionAgreement, AdoptionApplication, AdoptionFollowUp, AdoptionHandover, AdoptionPet
from app.repositories.adoption_repo import AdoptionRepository
from app.schemas.adoption import (
    AdoptionApplicationCreateIn,
    AdoptionApplicationDecisionIn,
    AdoptionAgreementCreateIn,
    AdoptionFollowUpCreateIn,
    AdoptionHandoverCreateIn,
    AdoptionPetCreateIn,
)
from app.services.merchant_service import MerchantService


FOLLOW_UP_PLAN_DAYS: dict[str, int] = {
    "day_7": 7,
    "day_30": 30,
    "day_90": 90,
    "half_year": 180,
    "one_year": 365,
}


class AdoptionService:
    def __init__(self, db: Session):
        self.repo = AdoptionRepository(db)
        self.merchant_service = MerchantService(db)

    def list_public(self, page: PageParams) -> tuple[list[AdoptionPet], int]:
        return self.repo.list_public(page)

    def list_mine(self, user_id: int) -> list[AdoptionPet]:
        return self.repo.list_mine(user_id)

    def create_pet(self, user_id: int, payload: AdoptionPetCreateIn) -> AdoptionPet:
        if payload.merchant_id is not None:
            merchant = self.merchant_service.get_owned(user_id, payload.merchant_id)
            if merchant.audit_status != "approved":
                raise AppException(ErrorCode.forbidden, "商家或机构入驻未审核通过，不能发布领养信息", 403)
        pet = AdoptionPet(publisher_id=user_id, audit_status="pending", **payload.model_dump())
        return self.repo.create(pet)

    def get_public_pet(self, pet_id: int) -> AdoptionPet:
        pet = self.repo.get_public_pet(pet_id)
        if pet is None:
            raise AppException(ErrorCode.not_found, "领养宠物不存在或未通过审核", 404)
        return pet

    def get_owned_pet(self, user_id: int, pet_id: int) -> AdoptionPet:
        pet = self.repo.get_pet(pet_id)
        if pet is None or pet.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "领养宠物不存在", 404)
        if pet.publisher_id != user_id:
            raise AppException(ErrorCode.forbidden, "无权查看该领养信息", 403)
        return pet

    def apply(self, user_id: int, payload: AdoptionApplicationCreateIn) -> AdoptionApplication:
        if payload.adoption_pet_id is None:
            raise AppException(ErrorCode.validation_error, "缺少领养宠物 ID", 400)
        pet = self.get_public_pet(payload.adoption_pet_id)
        if pet.publisher_id == user_id:
            raise AppException(ErrorCode.conflict, "不能申请自己发布的领养信息", 409)
        application = AdoptionApplication(applicant_id=user_id, **payload.model_dump())
        return self.repo.create(application)

    def list_my_applications(self, user_id: int) -> list[AdoptionApplication]:
        return self.repo.list_my_applications(user_id)

    def list_received_applications(self, user_id: int) -> list[AdoptionApplication]:
        return self.repo.list_received_applications(user_id)

    def approve_application(
        self, user_id: int, application_id: int, payload: AdoptionApplicationDecisionIn
    ) -> AdoptionApplication:
        application = self.get_received_application(user_id, application_id)
        application.audit_status = "approved"
        application.audit_reason = payload.reason
        application.audited_by = user_id
        application.audited_at = datetime.now(timezone.utc)
        application.status = "approved"
        return self.repo.save(application)

    def reject_application(
        self, user_id: int, application_id: int, payload: AdoptionApplicationDecisionIn
    ) -> AdoptionApplication:
        application = self.get_received_application(user_id, application_id)
        application.audit_status = "rejected"
        application.audit_reason = payload.reason or "领养申请未通过"
        application.audited_by = user_id
        application.audited_at = datetime.now(timezone.utc)
        application.status = "rejected"
        return self.repo.save(application)

    def get_received_application(self, user_id: int, application_id: int) -> AdoptionApplication:
        application = self.repo.get_application(application_id)
        if application is None or application.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "领养申请不存在", 404)
        pet = self.repo.get_pet(application.adoption_pet_id)
        if pet is None or pet.deleted_at is not None or pet.publisher_id != user_id:
            raise AppException(ErrorCode.forbidden, "无权处理该领养申请", 403)
        return application

    def create_or_update_agreement(
        self, user_id: int, application_id: int, payload: AdoptionAgreementCreateIn
    ) -> AdoptionAgreement:
        application = self.get_received_application(user_id, application_id)
        if application.audit_status != "approved":
            raise AppException(ErrorCode.conflict, "领养申请通过后才能绑定协议", 409)
        agreement = self.repo.get_agreement_by_application(application_id)
        if agreement is None:
            agreement = AdoptionAgreement(application_id=application_id, **payload.model_dump())
        else:
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(agreement, field, value)
        application.status = "agreement_signed"
        self.repo.save(application)
        return self.repo.save(agreement)

    def get_agreement(self, user_id: int, application_id: int) -> AdoptionAgreement:
        application = self.repo.get_application(application_id)
        if application is None or application.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "领养申请不存在", 404)
        pet = self.repo.get_pet(application.adoption_pet_id)
        if application.applicant_id != user_id and (pet is None or pet.publisher_id != user_id):
            raise AppException(ErrorCode.forbidden, "无权查看该领养协议", 403)
        agreement = self.repo.get_agreement_by_application(application_id)
        if agreement is None:
            raise AppException(ErrorCode.not_found, "领养协议不存在", 404)
        return agreement

    def create_or_update_handover(
        self, user_id: int, application_id: int, payload: AdoptionHandoverCreateIn
    ) -> AdoptionHandover:
        application = self.get_received_application(user_id, application_id)
        if application.audit_status != "approved":
            raise AppException(ErrorCode.conflict, "领养申请通过后才能记录交接", 409)
        handover = self.repo.get_handover_by_application(application_id)
        if handover is None:
            handover = AdoptionHandover(application_id=application_id, **payload.model_dump())
        else:
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(handover, field, value)
        application.status = "handover_completed"
        self.repo.save(application)
        handover = self.repo.save(handover)
        if handover.status == "completed":
            self.generate_follow_up_plan(application.id, handover.handover_at)
        return handover

    def get_handover(self, user_id: int, application_id: int) -> AdoptionHandover:
        application = self.repo.get_application(application_id)
        if application is None or application.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "领养申请不存在", 404)
        pet = self.repo.get_pet(application.adoption_pet_id)
        if application.applicant_id != user_id and (pet is None or pet.publisher_id != user_id):
            raise AppException(ErrorCode.forbidden, "无权查看该交接记录", 403)
        handover = self.repo.get_handover_by_application(application_id)
        if handover is None:
            raise AppException(ErrorCode.not_found, "交接记录不存在", 404)
        return handover

    def generate_follow_up_plan(
        self, application_id: int, handover_at: datetime | None = None
    ) -> list[AdoptionFollowUp]:
        base_time = handover_at or datetime.now(timezone.utc)
        created_or_existing: list[AdoptionFollowUp] = []
        for follow_up_type, days in FOLLOW_UP_PLAN_DAYS.items():
            existing = self.repo.get_follow_up_by_type(application_id, follow_up_type)
            if existing is not None:
                created_or_existing.append(existing)
                continue
            follow_up = AdoptionFollowUp(
                application_id=application_id,
                follow_up_type=follow_up_type,
                planned_at=base_time + timedelta(days=days),
                status="pending",
            )
            created_or_existing.append(self.repo.create(follow_up))
        return created_or_existing

    def create_follow_up(self, user_id: int, payload: AdoptionFollowUpCreateIn) -> AdoptionFollowUp:
        application = self.repo.get_application(payload.application_id)
        if application is None or application.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "领养申请不存在", 404)
        pet = self.repo.get_pet(application.adoption_pet_id)
        if pet is None or pet.publisher_id != user_id:
            raise AppException(ErrorCode.forbidden, "无权创建该回访记录", 403)
        follow_up = AdoptionFollowUp(**payload.model_dump())
        return self.repo.create(follow_up)

    def list_follow_ups(self, user_id: int, application_id: int) -> list[AdoptionFollowUp]:
        application = self.repo.get_application(application_id)
        if application is None or application.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "领养申请不存在", 404)
        pet = self.repo.get_pet(application.adoption_pet_id)
        if application.applicant_id != user_id and (pet is None or pet.publisher_id != user_id):
            raise AppException(ErrorCode.forbidden, "无权查看该回访记录", 403)
        return self.repo.list_follow_ups(application_id)
