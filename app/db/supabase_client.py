# app/db/supabase_client.py

from supabase import create_client, Client
from functools import lru_cache
from app.config.settings import get_settings

settings = get_settings()

@lru_cache()
def get_supabase_client() -> Client:
    """
    Supabase client using service_role for full backend access.
    RLS will be bypassed for all backend operations.
    """
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,     
    )
    return supabase
