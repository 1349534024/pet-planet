from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.models.user import User
from app.schemas.service_booking import (
    ServiceBookingCreateIn,
    ServiceBookingOut,
    ServiceItemCreateIn,
    ServiceItemOut,
    ServiceReportCreateIn,
    ServiceReportOut,
    ServiceScheduleCreateIn,
    ServiceScheduleOut,
)
from app.services.service_booking_service import ServiceBookingService

router = APIRouter()


@router.get("/items")
def list_service_items(page: PageParams = Depends(get_page_params), db: Session = Depends(get_db)):
    items, total = ServiceBookingService(db).list_public_items(page)
    return page_response([ServiceItemOut.model_validate(item).model_dump() for item in items], page.page, page.page_size, total)


@router.post("/items")
def create_service_item(
    payload: ServiceItemCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = ServiceBookingService(db).create_item(current_user.id, payload)
    return success(ServiceItemOut.model_validate(item).model_dump())


@router.get("/merchants/{merchant_id}/items")
def list_merchant_items(
    merchant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = ServiceBookingService(db).list_merchant_items(current_user.id, merchant_id)
    return success([ServiceItemOut.model_validate(item).model_dump() for item in items])


@router.post("/items/{service_item_id}/schedules")
def add_schedule(
    service_item_id: int,
    payload: ServiceScheduleCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    schedule = ServiceBookingService(db).add_schedule(current_user.id, service_item_id, payload)
    return success(ServiceScheduleOut.model_validate(schedule).model_dump())


@router.get("/items/{service_item_id}/schedules")
def list_schedules(service_item_id: int, db: Session = Depends(get_db)):
    items = ServiceBookingService(db).list_schedules(service_item_id)
    return success([ServiceScheduleOut.model_validate(item).model_dump() for item in items])


@router.post("")
def create_booking(
    payload: ServiceBookingCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = ServiceBookingService(db).create_booking(current_user.id, payload)
    return success(ServiceBookingOut.model_validate(booking).model_dump())


@router.get("/me")
def list_my_bookings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = ServiceBookingService(db).list_my_bookings(current_user.id)
    return success([ServiceBookingOut.model_validate(item).model_dump() for item in items])


@router.post("/{booking_id}/confirm")
def confirm_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = ServiceBookingService(db).confirm_booking(current_user.id, booking_id)
    return success(ServiceBookingOut.model_validate(booking).model_dump())


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = ServiceBookingService(db).cancel_booking(current_user.id, booking_id)
    return success(ServiceBookingOut.model_validate(booking).model_dump())


@router.post("/{booking_id}/complete")
def complete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = ServiceBookingService(db).complete_booking(current_user.id, booking_id)
    return success(ServiceBookingOut.model_validate(booking).model_dump())


@router.post("/{booking_id}/reports")
def create_report(
    booking_id: int,
    payload: ServiceReportCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = ServiceBookingService(db).create_report(current_user.id, booking_id, payload)
    return success(ServiceReportOut.model_validate(report).model_dump())


@router.get("/{booking_id}/reports")
def list_reports(booking_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = ServiceBookingService(db).list_reports(current_user.id, booking_id)
    return success([ServiceReportOut.model_validate(item).model_dump() for item in items])
