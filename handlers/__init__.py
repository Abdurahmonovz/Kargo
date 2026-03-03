from .start import router as start_router
from .order import router as order_router
from .payment import router as payment_router
from .admin import router as admin_router

__all__ = ["start_router", "order_router", "payment_router", "admin_router"]