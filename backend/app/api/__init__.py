from .products import router as products_router
from .price_history import router as price_history_router
from .alerts import router as alerts_router

__all__ = ["products_router", "price_history_router", "alerts_router"]
