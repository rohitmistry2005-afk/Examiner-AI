from fastapi import APIRouter

from app.config import get_settings
from app.db.supabase import get_supabase_client
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get("/db", response_model=DatabaseHealthResponse)
def database_health() -> DatabaseHealthResponse:
    try:
        client = get_supabase_client()
        # The health_check table will be created in Phase 2.
        response = client.table("health_check").select("id").limit(1).execute()
        return DatabaseHealthResponse(
            status="ok",
            database="supabase",
            detail=f"reachable; rows={len(response.data or [])}",
        )
    except Exception as exc:
        return DatabaseHealthResponse(
            status="error",
            database="supabase",
            detail=str(exc),
        )
