import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.analyze import router as analyze_router
from app.routes.Jobs import router as jobs_router
from app.database import get_db_health


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - TestGen AI 2026 - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 STARTUP
    logger.info("Starting TestGen AI API...")
    get_db_health()

    yield

    # 🔹 SHUTDOWN
    logger.info("Shutting down TestGen AI API...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint - used by load balancer"""
    db_health = get_db_health()

    is_healthy = db_health["status"] == "connected"

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": {
            "database": db_health["status"],
        },
    }


app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(jobs_router)
