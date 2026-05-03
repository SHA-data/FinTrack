from werkzeug.security import generate_password_hash, check_password_hash
from db import get_client
from postgrest.exceptions import APIError

TABLE = 'users'

def create_user(username, email, password):
    """
    Hashes the password and inserts a new user record into Supabase.
    Raises ValueError if email or username already exists.
    """
    client = get_client()
    hashed_password = generate_password_hash(password)
    
    try:
        response = client.table(TABLE).insert({
            'username': username,
            'email': email,
            'password_hash': hashed_password
        }).execute()
        return response.data[0]
    except APIError as e:
        # Check for unique constraint violation (often 23505 in Postgres)
        if 'already exists' in str(e).lower() or 'unique' in str(e).lower():
            raise ValueError("Email or username already exists.")
        raise e

def get_user_by_email(email):
    """
    Queries users table by email and returns the user dict or None.
    """
    client = get_client()
    try:
        response = client.table(TABLE).select('*').eq('email', email).single().execute()
        return response.data
    except APIError:
        # single() raises error if not found
        return None

def verify_password(plain_password, stored_hash):
    """
    Checks the plain password against stored hash.
    """
    return check_password_hash(stored_hash, plain_password)
