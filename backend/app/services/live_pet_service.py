from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.live_pet import LivePet, LivePetCertificate, LivePetMedia
from app.repositories.live_pet_repo import LivePetRepository
from app.schemas.live_pet import (
    LivePetAuditStatusOut,
    LivePetCertificateCreateIn,
    LivePetCreateIn,
    LivePetMediaCreateIn,
)
from app.services.merchant_service import MerchantService


LIVE_PET_MERCHANT_TYPES = {"pet_shop", "cattery", "kennel"}
HEALTH_CERTIFICATE_TYPE = "health_certificate"
QUARANTINE_CERTIFICATE_TYPE = "quarantine_certificate"


class LivePetService:
    def __init__(self, db: Session):
        self.repo = LivePetRepository(db)
        self.merchant_service = MerchantService(db)

    def list_public(self, page: PageParams) -> tuple[list[LivePet], int]:
        return self.repo.list_public(page)

    def list_mine(self, user_id: int) -> list[LivePet]:
        return self.repo.list_mine(user_id)

    def create(self, user_id: int, payload: LivePetCreateIn) -> LivePet:
        merchant = self.merchant_service.get_owned(user_id, payload.merchant_id)
        if merchant.audit_status != "approved":
            raise AppException(ErrorCode.forbidden, "商家入驻未审核通过，不能发布活体宠物", 403)
        if merchant.merchant_type not in LIVE_PET_MERCHANT_TYPES:
            raise AppException(ErrorCode.forbidden, "当前商家类型不能发布活体宠物", 403)
        live_pet = LivePet(publisher_id=user_id, audit_status="pending", status="draft", **payload.model_dump())
        return self.repo.create(live_pet)

    def get_public(self, live_pet_id: int) -> LivePet:
        live_pet = self.repo.get(live_pet_id)
        if live_pet is None or live_pet.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "活体宠物不存在", 404)
        if (
            live_pet.audit_status != "approved"
            or live_pet.status != "active"
            or not self._is_ready_for_audit(live_pet)
        ):
            raise AppException(ErrorCode.not_found, "活体宠物不存在或未通过审核", 404)
        return live_pet

    def get_audit_status(self, user_id: int, live_pet_id: int) -> LivePetAuditStatusOut:
        live_pet = self.get_owned(user_id, live_pet_id)
        media = self.repo.list_media(live_pet_id)
        certificates = self.repo.list_certificates(live_pet_id)
        certificate_types = {item.certificate_type for item in certificates if item.status == "active"}

        has_media = any(item.status == "active" for item in media)
        has_health_certificate = HEALTH_CERTIFICATE_TYPE in certificate_types
        has_quarantine_certificate = QUARANTINE_CERTIFICATE_TYPE in certificate_types
        has_vaccine_info = self._has_required_text(live_pet.vaccine_status)
        has_deworm_info = self._has_required_text(live_pet.deworm_status)

        missing_requirements: list[str] = []
        if not has_media:
            missing_requirements.append("media")
        if not has_health_certificate:
            missing_requirements.append(HEALTH_CERTIFICATE_TYPE)
        if not has_quarantine_certificate:
            missing_requirements.append(QUARANTINE_CERTIFICATE_TYPE)
        if not has_vaccine_info:
            missing_requirements.append("vaccine_status")
        if not has_deworm_info:
            missing_requirements.append("deworm_status")

        ready_for_audit = not missing_requirements
        can_be_listed = ready_for_audit and live_pet.audit_status == "approved" and live_pet.status == "active"
        return LivePetAuditStatusOut(
            id=live_pet.id,
            audit_status=live_pet.audit_status,
            audit_reason=live_pet.audit_reason,
            status=live_pet.status,
            has_media=has_media,
            has_health_certificate=has_health_certificate,
            has_quarantine_certificate=has_quarantine_certificate,
            has_vaccine_info=has_vaccine_info,
            has_deworm_info=has_deworm_info,
            ready_for_audit=ready_for_audit,
            can_be_listed=can_be_listed,
            missing_requirements=missing_requirements,
        )

    def get_owned(self, user_id: int, live_pet_id: int) -> LivePet:
        live_pet = self.repo.get(live_pet_id)
        if live_pet is None or live_pet.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "活体宠物不存在", 404)
        if live_pet.publisher_id != user_id:
            raise AppException(ErrorCode.forbidden, "无权操作该活体宠物", 403)
        return live_pet

    def add_media(self, user_id: int, live_pet_id: int, payload: LivePetMediaCreateIn) -> LivePetMedia:
        self.get_owned(user_id, live_pet_id)
        media = LivePetMedia(live_pet_id=live_pet_id, **payload.model_dump())
        return self.repo.create(media)

    def list_media(self, user_id: int, live_pet_id: int) -> list[LivePetMedia]:
        self.get_owned(user_id, live_pet_id)
        return self.repo.list_media(live_pet_id)

    def add_certificate(
        self, user_id: int, live_pet_id: int, payload: LivePetCertificateCreateIn
    ) -> LivePetCertificate:
        self.get_owned(user_id, live_pet_id)
        certificate = LivePetCertificate(live_pet_id=live_pet_id, **payload.model_dump())
        return self.repo.create(certificate)

    def list_certificates(self, user_id: int, live_pet_id: int) -> list[LivePetCertificate]:
        self.get_owned(user_id, live_pet_id)
        return self.repo.list_certificates(live_pet_id)

    def _has_required_text(self, value: str | None) -> bool:
        return value is not None and value.strip() != "" and value != "unknown"

    def _is_ready_for_audit(self, live_pet: LivePet) -> bool:
        media = self.repo.list_media(live_pet.id)
        certificates = self.repo.list_certificates(live_pet.id)
        certificate_types = {item.certificate_type for item in certificates if item.status == "active"}
        return (
            any(item.status == "active" for item in media)
            and HEALTH_CERTIFICATE_TYPE in certificate_types
            and QUARANTINE_CERTIFICATE_TYPE in certificate_types
            and self._has_required_text(live_pet.vaccine_status)
            and self._has_required_text(live_pet.deworm_status)
        )
