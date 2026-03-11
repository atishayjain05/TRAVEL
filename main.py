"""
FoodScout AI — FastAPI Application Entry Point
"""

import os
import sys

# Ensure project root is in the Python path so 'backend.*' imports resolve.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config import get_settings
from backend.database import init_db, check_db_connection
from backend.api.scan_routes import router as scan_router
from backend.api.restaurant_routes import router as restaurant_router
from backend.api.export_routes import router as export_router

settings = get_settings()

# ── App Factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="FoodScout AI",
    description="Automated restaurant discovery platform powered by AI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(scan_router)
app.include_router(restaurant_router)
app.include_router(export_router)

# ── Startup / Shutdown ────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    logger.info("FoodScout AI starting up...")
    if check_db_connection():
        logger.info("Database connection OK")
        try:
            init_db()
        except Exception as e:
            logger.warning(f"DB init warning (may already exist): {e}")
    else:
        logger.error("Database connection FAILED — check DATABASE_URL in .env")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("FoodScout AI shutting down.")


# ── Health & Root ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "FoodScout AI", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health():
    db_ok = check_db_connection()
    return JSONResponse(
        content={
            "status": "healthy" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
        },
        status_code=200 if db_ok else 503,
    )


# ── Dev server ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
