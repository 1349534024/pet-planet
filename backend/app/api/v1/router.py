from fastapi import APIRouter

from app.api.v1 import (
    adoption_applications,
    adoptions,
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
