from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .api import products_router
from .api.parser_configs import router as parser_configs_router

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Price Tracker API - Monitor your wishlist prices across e-commerce platforms",
)

# CORS (pour le frontend Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router, prefix=settings.API_PREFIX)
app.include_router(parser_configs_router, prefix=settings.API_PREFIX)

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.API_VERSION}

@app.get("/")
def root():
    return {
        "message": "Price Tracker API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
