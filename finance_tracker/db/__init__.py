from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def get_client() -> Client:
    """
    Initialises and returns a new Supabase client.
    The client is stateless and safe to initialise per-request.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)
