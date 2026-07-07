from fastapi import APIRouter

from app.api.v1 import (
    adoption_applications,
    adoptions,
    admin_audit,
    auth,
    cart,
    files,
    live_pets,
    merchants,
    orders,
    payments,
    pets,
    products,
    reminders,
    roles,
    service_bookings,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(pets.router, prefix="/pets", tags=["pets"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(adoptions.router, prefix="/adoptions", tags=["adoptions"])
api_router.include_router(
    adoption_applications.router,
    prefix="/adoption-applications",
    tags=["adoption_applications"],
)
api_router.include_router(live_pets.router, prefix="/live-pets", tags=["live_pets"])
api_router.include_router(service_bookings.router, prefix="/service-bookings", tags=["service_bookings"])
api_router.include_router(admin_audit.admin_user_router, prefix="/admin/users", tags=["admin"])
api_router.include_router(admin_audit.admin_role_router, prefix="/admin/roles", tags=["admin"])
api_router.include_router(admin_audit.admin_permission_router, prefix="/admin/permissions", tags=["admin"])
api_router.include_router(admin_audit.router, prefix="/admin/audit", tags=["admin-audit"])
api_router.include_router(admin_audit.risk_event_router, prefix="/risk/events", tags=["risk"])
api_router.include_router(admin_audit.risk_rule_router, prefix="/admin/risk/rules", tags=["risk"])
api_router.include_router(admin_audit.report_router, prefix="/admin/reports", tags=["reports"])
api_router.include_router(admin_audit.blacklist_router, prefix="/admin/blacklist", tags=["risk"])
api_router.include_router(admin_audit.message_router, prefix="/messages", tags=["messages"])
api_router.include_router(admin_audit.message_template_router, prefix="/admin/message-templates", tags=["messages"])
api_router.include_router(admin_audit.notification_router, prefix="/admin/notifications", tags=["messages"])
api_router.include_router(admin_audit.config_router, prefix="/admin/configs", tags=["operation-configs"])
api_router.include_router(admin_audit.statistics_router, prefix="/admin/statistics", tags=["statistics"])
