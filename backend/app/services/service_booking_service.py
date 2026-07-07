from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.pet import PetProfile
from app.models.service_booking import ServiceBooking, ServiceItem, ServiceReport, ServiceSchedule
from app.repositories.service_booking_repo import ServiceBookingRepository
from app.schemas.service_booking import (
    ServiceBookingCreateIn,
    ServiceItemCreateIn,
    ServiceReportCreateIn,
    ServiceScheduleCreateIn,
)
from app.services.merchant_service import MerchantService


class ServiceBookingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ServiceBookingRepository(db)
        self.merchant_service = MerchantService(db)

    def list_public_items(self, page: PageParams) -> tuple[list[ServiceItem], int]:
        return self.repo.list_public_items(page)

    def create_item(self, user_id: int, payload: ServiceItemCreateIn) -> ServiceItem:
        self.merchant_service.get_owned(user_id, payload.merchant_id)
        item = ServiceItem(**payload.model_dump())
        return self.repo.create(item)

    def list_merchant_items(self, user_id: int, merchant_id: int) -> list[ServiceItem]:
        self.merchant_service.get_owned(user_id, merchant_id)
        return self.repo.list_merchant_items(merchant_id)

    def get_owned_item(self, user_id: int, service_item_id: int) -> ServiceItem:
        item = self.repo.get(ServiceItem, service_item_id)
        if item is None or item.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "服务项目不存在", 404)
        self.merchant_service.get_owned(user_id, item.merchant_id)
        return item

    def add_schedule(self, user_id: int, service_item_id: int, payload: ServiceScheduleCreateIn) -> ServiceSchedule:
        self.get_owned_item(user_id, service_item_id)
        if payload.end_at <= payload.start_at:
            raise AppException(ErrorCode.validation_error, "结束时间必须晚于开始时间", 400)
        schedule = ServiceSchedule(service_item_id=service_item_id, **payload.model_dump())
        return self.repo.create(schedule)

    def list_schedules(self, service_item_id: int) -> list[ServiceSchedule]:
        item = self.repo.get(ServiceItem, service_item_id)
        if item is None or item.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "服务项目不存在", 404)
        return self.repo.list_schedules(service_item_id)

    def create_booking(self, user_id: int, payload: ServiceBookingCreateIn) -> ServiceBooking:
        item = self.repo.get(ServiceItem, payload.service_item_id)
        if item is None or item.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "服务项目不存在", 404)
        if item.audit_status != "approved" or item.status != "active":
            raise AppException(ErrorCode.conflict, "服务项目未审核通过或未上架，暂不能预约", 409)
        if payload.pet_id is not None:
            pet = self.db.get(PetProfile, payload.pet_id)
            if pet is None or pet.deleted_at is not None or pet.user_id != user_id:
                raise AppException(ErrorCode.pet_permission_denied, "无权使用该宠物档案预约", 403)
        if payload.schedule_id is not None:
            schedule = self.repo.get(ServiceSchedule, payload.schedule_id)
            if schedule is None or schedule.service_item_id != payload.service_item_id:
                raise AppException(ErrorCode.not_found, "服务排期不存在", 404)
            if schedule.status != "available":
                raise AppException(ErrorCode.conflict, "该排期不可预约", 409)
            if schedule.booked_count >= schedule.capacity:
                raise AppException(ErrorCode.conflict, "该排期已约满", 409)
            schedule.booked_count += 1
            self.repo.save(schedule)
        booking = ServiceBooking(user_id=user_id, **payload.model_dump())
        return self.repo.create(booking)

    def list_my_bookings(self, user_id: int) -> list[ServiceBooking]:
        return self.repo.list_my_bookings(user_id)

    def confirm_booking(self, user_id: int, booking_id: int) -> ServiceBooking:
        booking = self._get_owned_merchant_booking(user_id, booking_id)
        if booking.status != "submitted":
            raise AppException(ErrorCode.conflict, "只有待确认预约可以确认", 409)
        booking.status = "confirmed"
        return self.repo.save(booking)

    def cancel_booking(self, user_id: int, booking_id: int) -> ServiceBooking:
        booking = self._get_booking(booking_id)
        if booking.user_id != user_id:
            self._ensure_merchant_can_handle_booking(user_id, booking)
        if booking.status in {"completed", "reported", "canceled"}:
            raise AppException(ErrorCode.conflict, "当前预约状态不能取消", 409)
        booking.status = "canceled"
        self._release_schedule_capacity(booking)
        return self.repo.save(booking)

    def complete_booking(self, user_id: int, booking_id: int) -> ServiceBooking:
        booking = self._get_owned_merchant_booking(user_id, booking_id)
        if booking.status != "confirmed":
            raise AppException(ErrorCode.conflict, "只有已确认预约可以完成", 409)
        booking.status = "completed"
        return self.repo.save(booking)

    def create_report(self, user_id: int, booking_id: int, payload: ServiceReportCreateIn) -> ServiceReport:
        booking = self._get_owned_merchant_booking(user_id, booking_id)
        if booking.status not in {"completed", "reported"}:
            raise AppException(ErrorCode.conflict, "服务完成后才能提交服务报告", 409)
        report = ServiceReport(booking_id=booking.id, reporter_id=user_id, **payload.model_dump())
        booking.status = "reported"
        self.repo.save(booking)
        return self.repo.create(report)

    def list_reports(self, user_id: int, booking_id: int) -> list[ServiceReport]:
        booking = self.repo.get(ServiceBooking, booking_id)
        if booking is None or booking.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "预约不存在", 404)
        if booking.user_id != user_id:
            self.get_owned_item(user_id, booking.service_item_id)
        return self.repo.list_reports(booking_id)

    def _get_booking(self, booking_id: int) -> ServiceBooking:
        booking = self.repo.get(ServiceBooking, booking_id)
        if booking is None or booking.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "预约不存在", 404)
        return booking

    def _get_owned_merchant_booking(self, user_id: int, booking_id: int) -> ServiceBooking:
        booking = self._get_booking(booking_id)
        self._ensure_merchant_can_handle_booking(user_id, booking)
        return booking

    def _ensure_merchant_can_handle_booking(self, user_id: int, booking: ServiceBooking) -> None:
        self.get_owned_item(user_id, booking.service_item_id)

    def _release_schedule_capacity(self, booking: ServiceBooking) -> None:
        if booking.schedule_id is None:
            return
        schedule = self.repo.get(ServiceSchedule, booking.schedule_id)
        if schedule is None:
            return
        if schedule.booked_count > 0:
            schedule.booked_count -= 1
            self.repo.save(schedule)
