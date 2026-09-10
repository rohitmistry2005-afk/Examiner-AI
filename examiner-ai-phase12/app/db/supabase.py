from functools import lru_cache

from app.config import get_settings
from app.core.exceptions import ConfigurationError


@lru_cache
def get_supabase_client():
    """Create the server-side Supabase client lazily.

    Keeping the import and client creation lazy allows the API application and
    health endpoint to start even before the Supabase dependency is installed
    or credentials are configured. Database-dependent operations fail clearly.
    """
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ConfigurationError("Supabase is not configured.")

    try:
        from supabase import create_client
    except ImportError as exc:
        raise ConfigurationError("The 'supabase' package is not installed.") from exc

    return create_client(settings.supabase_url, settings.supabase_service_role_key)
