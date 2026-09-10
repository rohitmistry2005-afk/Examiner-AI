from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.documents import router as document_router
from app.api.exams import router as exams_router
from app.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered adaptive technical examination backend for ExaminerAI.",
    lifespan=lifespan,
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(document_router, prefix=settings.api_prefix)
app.include_router(exams_router, prefix=settings.api_prefix)
